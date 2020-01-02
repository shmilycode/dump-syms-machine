## 使用方法

将该脚本拷贝到与需要生成符号文件的文件夹同一目录下，在不同目录下运行会出错，然后指定source和destination，这两个都必须是相对路径

参数：

@dump_syms: 指定dump_syms可执行文件的路径

@source: 指定需要导出符号表的文件夹的名称，程序会遍历文件夹下所有的动态链接库并逐个生成符号文件

@destination: 生成的符号文件存放的路径

''' shell

python dump_syms_machine.py --dump_syms /mnt/hgfs/code/breakpad/src/src/tools/linux/dump_syms/dump_syms --source system --destination symbols

'''