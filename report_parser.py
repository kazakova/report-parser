from os import listdir, path
import sys
import argparse

class bcolors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
def file_parser(path_to_file, thr):
    file = path.basename(path_to_file)
    
    with open(path_to_file) as f:
        name = file.split('.WGS')[0]
        cont_flag = False
        war_1 = False
        war_2 = False
        
        for s in f.readlines():
            if 'Mean Coverage' in s:
                cov = s.split('\t')[1].split('\n')[0]
                
            if 'Contamination.Status' in s:
                cont_flag = True
                
            if cont_flag and name in s:
                cont_status = s.split('\t')[1]
                cont_flag = False
                
        if (float(cov) < thr) or (cont_status == 'YES'):
            war_1 = True
        elif cont_status == 'ND':
            war_2 = True
            
    tmp_list = [name, cov, cont_status, war_1, war_2]           
    return tmp_list

def folder_parser(path_to_folder, paths):
    for f in listdir(path_to_folder):
        path_to_f = path.join(path_to_folder, f)
        if path.isdir(path_to_f):
            tmp_paths = folder_parser(path_to_f, paths)
            if type(tmp_paths) == str:
                paths.update([tmp_paths])
            elif type(tmp_paths) == list:
                paths.update(tmp_paths)
        elif f.endswith('report.tsv'):
            path_to_report = path.join(path_to_folder, f)
            return path_to_report
        
    return paths

def printer(headers, data):
    print('\t'.join(headers))
    for i in data:
        if i[3] == True:
            print(bcolors.FAIL + '\t'.join(i[:3]) + bcolors.ENDC)
        elif i[4] == True:
            print(bcolors.WARNING + '\t'.join(i[:3]) + bcolors.ENDC)
        else:
            print('\t'.join(i[:3]))    

def report_parser(args):
    common_list = []
    headers = ['sample', 'mean coverage', 'contamination status']
    
    paths = folder_parser(args.main_dir, set())
        
    for report_file in paths:
        common_list.append(file_parser(report_file, args.threshold))
        
    paths.clear()   
    printer(headers, common_list)
    common_list.clear()

pars = argparse.ArgumentParser(description = 'Script for checking contamination and coverage by WGS reports. If mean coverage < threshold or contamination status is "YES", the line is highlighted in red. If contamination status is "ND", the line is highlighted in yellow.')
pars.add_argument('--main-dir', help = 'Project folder')
pars.add_argument('--threshold', type = float, default = 30, help = 'Coverage threshold. Default is 30')
args = pars.parse_args()

report_parser(args)

   