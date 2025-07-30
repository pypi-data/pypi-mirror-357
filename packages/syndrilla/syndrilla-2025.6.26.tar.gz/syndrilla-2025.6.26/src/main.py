import torch
import re
import sys, os, time
import pyfiglet, argparse, time
import numpy as np
import csv
import yaml

import subprocess

from loguru import logger

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import bcolors
from src.decoder import create_decoder
from src.error_model import create_error_model
from src.syndrome import create_syndrome
from src.metric import report_metric, save_metric, compute_avg_metrics
from src.logical_check import create_check


def parse_commandline_args():
    """
    parse command line inputs
    """
    parser = argparse.ArgumentParser(
        description='The syndrilla is a framework to run decoding simulation.')
    parser.add_argument('-r', '--run_dir', type=str, default='tests/test_outputs',
                        help = 'The run directory to store outputs.')
    parser.add_argument('-d', '--decoder_yaml', type=str, default=None,
                        help = 'Path to decoder yaml.')
    parser.add_argument('-e', '--error_yaml', type=str, default=None,
                        help = 'Path to error model yaml.')
    parser.add_argument('-c', '--logical_yaml', type=str, default=None,
                        help = 'Path to logical error check yaml.')
    parser.add_argument('-s', '--syndrome_yaml', type=str, default=None,
                        help = 'Path to syndrome yaml.')
    parser.add_argument('-bs', '--batch_size', type=int, default=1000,
                        help = 'The number of samples run each batch.')
    parser.add_argument('-ss', '--sample_size', type=int, default=1000,
                        help = 'The total number of samples to run.')
    parser.add_argument('-l', '--log_level', type=str, default='INFO',
                        help = 'Level of logger.')
    parser.add_argument('-o', '--output_yaml', type=str, default='INFO',
                        help = 'Path to save method yaml.')

    return parser.parse_args()


def save_metrics_to_csv(csv_path, row_dict, fieldnames):
    """
    Save one row of metrics to a CSV file. Creates a new file with a header
    if one doesn't already exist, otherwise appends to the existing file.
    """
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)


def main():
    args = parse_commandline_args()
    
    # set up output log
    logger.remove()
    output_log = args.run_dir + '/main' + '-' + str(time.time()) + '.log'
    logger.add(output_log, level=args.log_level)

    # set up banner
    ascii_banner = pyfiglet.figlet_format('SYNDRILLA')
    print(bcolors.Magenta + ascii_banner + bcolors.ENDC)
    ascii_banner = pyfiglet.figlet_format('UnaryLab')
    print(bcolors.Yellow + ascii_banner + bcolors.ENDC)
    ascii_banner = pyfiglet.figlet_format('https://github.com/UNARY-Lab/syndrilla', font='term')
    print(bcolors.UNDERLINE + bcolors.Green + ascii_banner + bcolors.ENDC)

    with open(args.output_yaml, 'r') as f:
        config = yaml.safe_load(f)
    save_error = config['output'].get('error_llr', False)
    logger.success(f'\n----------------------------------------------\nStep 1: Create decoder\n----------------------------------------------')
    decoders = create_decoder(args.decoder_yaml)
    
    num_decoders = len(decoders)
    algo_name = []
    for decoder in decoders:
        decoder.eval()
        algo_name.append(decoder.algo)
    shape = decoders[0].H_shape
    dtype = decoders[0].dtype
    decoder_device = decoders[0].device
    H_matrix = decoders[0].H_matrix
    if decoders[0].type.lower() == 'hx':
        l_matrix = decoders[0].lx_matrix
    else:
        l_matrix = decoders[0].lz_matrix

    num_batches = args.sample_size/args.batch_size

    e_v_all = [torch.empty((0, shape[1]), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
    e_all = torch.empty((0, shape[1]), dtype=dtype, device=decoder_device)
    
    converge_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
    iter_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
    time_iter_all = [[] for _ in range(num_decoders)]

    check = []
    if not save_error:
        total_time_all = [0.0 for _ in range(num_decoders)]
        average_time_sample_all = [0.0 for _ in range(num_decoders)]
        average_iter_all = [0.0 for _ in range(num_decoders)]
        average_time_sample_iter_all = [0.0 for _ in range(num_decoders)]
        data_qubit_acc_all = [0.0 for _ in range(num_decoders)]
        correction_acc_all = [0.0 for _ in range(num_decoders)]
        logical_error_rate_all = [0.0 for _ in range(num_decoders)]
        invoke_rate_all = [0.0 for _ in range(num_decoders)]
        
    for _ in range(int(num_batches)):
        logger.success(f'\n----------------------------------------------\nStep 2: Create error model\n----------------------------------------------')
        if not save_error: 
            e_v_all = [torch.empty((0, shape[1]), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
            e_all = torch.empty((0, shape[1]), dtype=dtype, device=decoder_device)
            
            converge_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
            iter_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
            time_iter_all = [[] for _ in range(num_decoders)]
 
        error_model = create_error_model(args.error_yaml)
        
        # create error
        zero_qubits = torch.zeros([args.batch_size, shape[1]], dtype=dtype)
        error_vector, error_dataloader = error_model.inject_error(zero_qubits, args.batch_size)

        avg_error_rate = torch.mean(torch.sum(error_vector, 1) / shape[1])
        logger.info(f'Specified error rate <{error_model.rate}>.')
        logger.info(f'Generated error rate <{avg_error_rate}>.')

        logger.success(f'\n----------------------------------------------\nStep 3: Create sydrome generator\n----------------------------------------------')
        syndrome_generator = create_syndrome(args.syndrome_yaml)

        logger.success(f'\n----------------------------------------------\nStep 4: Decode\n----------------------------------------------')
        
        for err, llr, _ in error_dataloader:
            # generate the syndrome for decoder
            err = err.to(e_all.device)
            e_all = torch.cat((e_all, err))
            synd = syndrome_generator.measure_syndrome(err, decoders[0])

            io_dict = {
                'synd': synd,
                'llr0': llr,
                'H_matrix': H_matrix
            }
            decoder_idx = 0
            
            if decoder_idx == 0:
            # first decoder
                start_time = time.time()
                io_dict = decoders[0](io_dict)

                time_iter_all[0].append(time.time() - start_time)
                
                e_v_all[0] = torch.cat((e_v_all[0], io_dict['e_v']), dim=0)
                iter_all[0] = torch.cat((iter_all[0], io_dict['iter']))
                converge_all[0] = torch.cat((converge_all[0], torch.zeros_like(io_dict['converge'])), dim=0)
                if decoder_idx + 1 < num_decoders:
                    converge_all[1] = torch.cat((converge_all[0], io_dict['converge']), dim=0)
                decoder_idx += 1
            while decoder_idx < num_decoders:
                # second decoder
                start_time = time.time()
                io_dict = decoders[1](io_dict)

                time_iter_all[decoder_idx].append(time.time() - start_time)
                e_v_all[decoder_idx] = torch.cat((e_v_all[decoder_idx], io_dict['e_v']), dim=0)
                iter_all[decoder_idx] = torch.cat((iter_all[decoder_idx], io_dict['iter']))
                if decoder_idx + 1 < num_decoders:
                    converge_all[decoder_idx] = torch.cat((converge_all[decoder_idx+1], io_dict['converge']), dim=0)
                decoder_idx += 1      
            
            if not save_error: 
                logger.success(f'\n----------------------------------------------\nStep 5: Check logical error rate\n----------------------------------------------')
                logical_check = create_check(yaml_path = './examples/alist/lx.check.yaml')
                check.append(logical_check.check(e_v_all[0], e_all, l_matrix))
                for i in range(1, num_decoders):
                    check.append(logical_check.check_osd(e_v_all[i], e_all, l_matrix, converge_all[i]))

                # # report metric
                logger.success(f'\n----------------------------------------------\nStep 6: Save log\n----------------------------------------------')
                for i in range(num_decoders):
                    batch_total_time, batch_average_time_sample, batch_average_iter, batch_average_time_sample_iter, batch_data_qubit_acc, batch_correction_acc, batch_logical_error_rate, batch_invoke_rate = report_metric(e_all, e_v_all[i], iter_all[i], time_iter_all[i], check[i], converge_all[i], i)
                    total_time_all[i] += batch_total_time
                    average_time_sample_all[i] += batch_average_time_sample
                    average_iter_all[i] += batch_average_iter
                    average_time_sample_iter_all[i] += batch_average_time_sample_iter
                    data_qubit_acc_all[i] += batch_data_qubit_acc
                    correction_acc_all[i] += batch_correction_acc
                    logical_error_rate_all[i] += batch_logical_error_rate
                    invoke_rate_all[i] += batch_invoke_rate
    
    all_metrics = []
    if save_error:
        logger.success(f'\n----------------------------------------------\nStep 5: Check logical error rate\n----------------------------------------------')
        logical_check = create_check(yaml_path = './examples/alist/lx.check.yaml')
        check.append(logical_check.check(e_v_all[0], e_all, l_matrix))
        for i in range(1, num_decoders):
            check.append(logical_check.check_osd(e_v_all[i], e_all, l_matrix, converge_all[i]))
        
        logger.success(f'\n----------------------------------------------\nStep 6: Save log\n----------------------------------------------')
        for i in range(num_decoders):
            total_time, average_time_sample, average_iter, average_time_sample_iter, data_qubit_acc, correction_acc, logical_error_rate, invoke_rate = report_metric(e_all, e_v_all[i], iter_all[i], time_iter_all[i], check[i], converge_all[i], i)
            metrics_dict = {
                'algorithm': algo_name[i],
                'total_time': total_time,
                'average_time_sample': average_time_sample,
                'average_iter': average_iter,
                'average_time_sample_iter': average_time_sample_iter,
                'data_qubit_acc': data_qubit_acc,
                'correction_acc': correction_acc,
                'logical_error_rate': logical_error_rate,
                'invoke_rate': invoke_rate
            }
            all_metrics.append(metrics_dict)
    else:
        logger.success(f'\n----------------------------------------------\nStep 6: Save Final log\n----------------------------------------------')
        for i in range(num_decoders):
            total_time, average_time_sample, average_iter, average_time_sample_iter, data_qubit_acc, \
                correction_acc, logical_error_rate, invoke_rate = compute_avg_metrics(args.sample_size, i, num_batches, total_time_all,
                                                                                average_time_sample_all,
                                                                                average_iter_all,
                                                                                average_time_sample_iter_all,
                                                                                data_qubit_acc_all,
                                                                                correction_acc_all,
                                                                                logical_error_rate_all,
                                                                                invoke_rate_all)
            metrics_dict = {
                'algorithm': algo_name[i],
                'total_time': total_time,
                'average_time_sample': average_time_sample,
                'average_iter': average_iter,
                'average_time_sample_iter': average_time_sample_iter,
                'data_qubit_acc': data_qubit_acc,
                'correction_acc': correction_acc,
                'logical_error_rate': logical_error_rate,
                'invoke_rate': invoke_rate
            }
            all_metrics.append(metrics_dict)

    logger.success(f'Saved log to <{output_log}>.')

    logger.success(f'\n----------------------------------------------\nStep 7: Save metric results\n----------------------------------------------')
    for i in range(num_decoders):
        save_metric(all_metrics, args.run_dir + '/', args.batch_size, args.sample_size, error_model.rate)
    
    logger.success(f'Saved results to <{output_log}>.')


if __name__ == '__main__':
    main()
