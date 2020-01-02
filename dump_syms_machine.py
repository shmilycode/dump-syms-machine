import os
import argparse
import logging
from logging import debug, info, warning, error, critical
import shutil
import multiprocessing

dump_symbols_bin = ""
tmp_folder = "tmp"

def do_dump_syms(lib_path, output_path):
  '''
  Run dump_syms command to convert library file to symbols file, 
  Return the hash code of symbols and full path of symbols file.
  @lib_path: the full path of library to dump.
  @output_path: the full path of symbol to store.
  '''
  lib_name = os.path.basename(lib_path)
  symbol_output = os.path.join(output_path, lib_name + ".sym")
  command = [dump_symbols_bin, lib_path, ">", symbol_output]
  command = " ".join(command)
  debug(command)
  os.system(command)
  hash_code = ""
  with open(symbol_output, 'r') as symbol_file:
    head = symbol_file.readline()
    hash_code = head.split()[3]
  return (hash_code, symbol_output)

def is_available_library(library_name):
  '''
  Check if name of library is available, normally, library name end with .so
  @library_name: Name of library
  '''
  if library_name.endswith(".so"):
    return True
  return False

def travel_directory(dir_to_travel):
  '''
  Travel the directory and return the file list with full path.
  '''
  list_dirs = os.walk(dir_to_travel)  

  lib_list = []
  for root, dirs, files in list_dirs:
    for lib_name in files:
      if is_available_library(lib_name):
        lib_path = os.path.join(root, lib_name)
        lib_list.append(lib_path)
        debug(lib_path)
  return lib_list

def dump_syms_process(lib_path):
  '''
  Do dump_syms to a specified library, symbols file will be 
  save in @tmp_folder with specified directory structure, which was needed by minidump_stackwalker,
  like "tmp/library_name/hash_code/symbol_file"
  '''
  tmp_lib_output_path = os.path.join(tmp_folder, lib_path)
  os.makedirs(tmp_lib_output_path)
  debug("Create directory %s" % tmp_lib_output_path)

  hash_code, symbol_output_path = do_dump_syms(lib_path, tmp_lib_output_path)
  info("%s %s" % (hash_code, symbol_output_path))

  #Move symbols file into specified directory, which name is the hash code of symbols file.
  tmp_lib_output_path = os.path.join(tmp_lib_output_path, hash_code)
  os.makedirs(tmp_lib_output_path)
  debug("Move %s to %s" % (symbol_output_path, tmp_lib_output_path))
  shutil.move(symbol_output_path, tmp_lib_output_path)

def dump_syms_in_multiprocess(input_folder, output_folder):
  if os.path.exists(tmp_folder):
    warning("Remove existed %s" % tmp_folder)
    shutil.rmtree(tmp_folder)
  
  library_path_list = travel_directory(input_folder)
  info("%d library need to dump."%len(library_path_list))

  cpu_count = multiprocessing.cpu_count()
  info("CPU count %d"%cpu_count)

  processor_pool = multiprocessing.Pool(cpu_count)
  processor_pool.map(dump_syms_process, library_path_list)
  processor_pool.close()
  processor_pool.join()
#  for lib in library_path_list:
#    dump_syms_process(lib)

  #Move symbols file from tmp to specified folder.
  tmp_files = os.listdir(tmp_folder)
  for tmp_file in tmp_files:
    output_file = os.path.join(output_folder, tmp_file)
    if os.path.exists(output_file):
      shutil.rmtree(output_file)
    debug("Copy %s to %s" % (tmp_file, output_folder))
    shutil.copytree(os.path.join(tmp_folder, tmp_file), output_file)

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument('--dump_syms')
  parser.add_argument('--source')
  parser.add_argument('--destination')
  args = parser.parse_args()

  dump_symbols_bin = args.dump_syms
  source = args.source
  destination = args.destination
  if not os.path.exists(source):
    raise Exception("%s not existed"%(source))
  if not os.path.exists(destination):
    os.makedirs(destination)
    debug("Create %s"%destination)
  dump_syms_in_multiprocess(source, args.destination)