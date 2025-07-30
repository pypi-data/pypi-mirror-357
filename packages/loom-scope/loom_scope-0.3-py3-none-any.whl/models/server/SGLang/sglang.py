import sys
import time
from copy import deepcopy

from loguru import logger
from transformers import AutoTokenizer
import sglang as sgl

from ...base.AccelerationModel import AccelerationModel
from ...utils.build_chat import RetrieveModelBuildChat

logger.remove()
logger.add(sys.stdout,colorize=True,format="<level>{message}</level>")

class SGLang(AccelerationModel):
    def __init__(self,model_path,torch_dtype,adapter_path,gp_num,max_model_len,gpu_memory_utilization,**kwargs):
        super().__init__(**kwargs)
        self.model_path= model_path
        self.torch_dtype = torch_dtype
        self.gp_num = gp_num
        self.adapter_path = adapter_path
        self.params_dict = {}
        self.max_model_len = max_model_len
        self.gpu_memory_utilization = gpu_memory_utilization
   
    def deploy(self):
        time_start = time.time()
        
        tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        
        # SGLang backend initialization
        backend_args = {
            "model_path": self.model_path,
            "tokenizer_path": self.model_path,
            "tp_size": self.gp_num,
            "trust_remote_code": True,
            "mem_fraction_static": self.gpu_memory_utilization,
        }
        
        if self.max_model_len:
            backend_args["context_length"] = self.max_model_len
            
        # Initialize SGLang backend
        backend = sgl.Engine(**backend_args)
        sgl.set_default_backend(backend)
        
        logger.info("SGLang model and tokenizer initialized.", flush=True)
        time_cost = time.time() - time_start
        logger.info("Model_deploy time :{}".format(time_cost), flush=True)
        
        return backend, tokenizer

    def updata_params(self, params, tokenizer, enable_thinking):
        params_ = deepcopy(self.params_dict)
        params_.update(params)
        
        # Remove parameters not supported by SGLang
        del_list = ["do_sample", "num_beams", "min_length", "max_length"]
        for i in del_list:
            if i in params_:
                params_.pop(i)
                
        if "temperature" in params_ and not params_["temperature"]:
            params_["temperature"] = 0.0

        del_list = []
        for i in params_:
            if not params_[i]:
                del_list.append(i)
        for i in del_list:
            params_.pop(i)
            
        default_params = {"temperature": 0.7, "top_p": 0.95, "max_new_tokens": 10000}
        default_params.update(params_)
        
        return default_params


    def generate(self,model,tokenizer,input,params,**kwargs):
        @sgl.function
        def generate_text(s, prompt):
            s += prompt
            s += sgl.gen("response", **params)
        
        state = generate_text.run(prompt=input_text)
        outputs = state["response"]
    
        if "</think>" not in outputs:
            return outputs 
        else:
            outputs = outputs.split("</think>")[-1].strip()
            return outputs


        








  