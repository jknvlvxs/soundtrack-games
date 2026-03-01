import subprocess
import sys

models = [
    ("/app/code/checkpoints", "GVMGen_Base"),
    ("/app/xps/audiocraft_gvmgen/xps/gvmgen_retrain_524c0212", "GVMGen_Retrain"),
    ("/app/xps/audiocraft_gvmgen/xps/gvmgen_tuned_0db722fd", "GVMGen_Tuned"),
]

script = '/app/code/test_suite.py'

for model in models:
    subprocess.run([sys.executable, script, "--state_dict_bin_folder", model[0], "--model_name", model[1]])