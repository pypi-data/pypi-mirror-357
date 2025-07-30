# 🐷 PyG interface 🐽 class for defining blocks

from abc import ABC, abstractmethod
import threading

# base class for PyG blocks
class BlockBase(ABC):
    """
    Block基类，强制子类只能接受flag_debug参数
    """
    @abstractmethod
    def __init__(self):
        """
        子类必须调用super().__init__(flag_debug)
        且不能添加其他参数
        """
        # self.flag_debug = flag_debug
        self.attrNamesArr = []  # 新增属性名称数组，用于存储属性名称
    
    # instance method for loading attributes to instance
    def read_parameters(self, parDict: dict) -> None:
        """Reads parameters from the model parameters file."""
        """
        从parDict中读取参数值
        :param parDict: 参数字典
        :raises: KeyError 如果缺少必需的参数
        """
        for attr_name in self.attrNamesArr:
            if attr_name not in parDict:
                raise KeyError(f"Missing required parameter: {attr_name}")
            setattr(self, attr_name, parDict[attr_name])
    
    @abstractmethod
    def read_inputs(self, inputs: list) -> None:
        """Read inputs to the block, 
        report errors if inputs are not valid.
        Even for blocks without inputs, this method
        is expected, even with a simple pass."""
        raise NotImplementedError("Subclasses must implement read_inputs()")
        
    @abstractmethod
    def compute_outputs(self, time: float) -> list:
        """
        计算输出，接收时间参数
        :param time: 当前时间
        :return: 输出列表
        """
        raise NotImplementedError("Subclasses must implement compute_outputs()")

    @abstractmethod
    def reset(self) -> None:
        """Reset internal states of the block.
         optional method, as some blocks may not need internal states"""
        pass

################ model coder part ####################
class MySampleBlock(BlockBase):
    
    def __init__(self):
        super().__init__()
        self.state = 0
        self.attrNamesArr = ["par1", "par2"]

    def read_inputs(self, inputs: list) -> None:
        if len(inputs) != 2: # check input validity
            raise ValueError("Inputs must be two numbers")
        self.input1 = inputs[0]
        self.input2 = inputs[1]
        
    def compute_outputs(self, time = None) -> list:
        self.state += 1 # internal states are allowed, and used here as an example
        self.outputs = [self.input1+self.input2, self.par1 + self.par2 + self.state]
        return self.outputs

    def reset(self) -> None:
        self.state = 0

# test code
if __name__ == "__main__":
    myBlock = MySampleBlock()
    parDict = {
        "par1": 1,
        "par2": 2,
    }
    myBlock.read_parameters(parDict)
    
    inputs = [3,4]
    myBlock.read_inputs(inputs)
    outputs = myBlock.compute_outputs() # time is not required for this block
    for _ in range(5): # internal states are allowed, and used here as an example
        outputs = myBlock.compute_outputs()
        print(outputs)
    
    myBlock.reset()
    outputs = myBlock.compute_outputs() # time is not required for this block
    print(outputs)