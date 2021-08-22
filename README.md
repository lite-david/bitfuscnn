# BitFuSCNN: A variable bitwidth compressed sparse CNN accelerator

Pruning a DNN model results in a lot of sparsity in weights and ReLU layer introduces sparsity in activations. The [SCNN accelerator](https://arxiv.org/abs/1708.04485) makes use of this fact to reduce the number of computations performed. DNNs can operate with reduced bitwidth without degradation in classification accuracy. The [BitFusion accelerator](https://arxiv.org/pdf/1712.01507.pdf) introduces a bitwidth - computation tradeoff to support different inference accelerator performance points. Lesser number of bits, more the number of computations per processing engine.  BitFuSCNN strives to combine the benefits of both sparsity and quantization in CNNs. The design is similar to that of SCNN, except the bitwidths are variable. Instead of a fixed 4x4 multiplier operating on 16 bit values like in SCNN, we have a variable bitwidth multiplier operating on 16x16, 8x8, or 4x4 input either 2, 4, or 8 bits wide.

[BitFuSCNN report](https://drive.google.com/file/d/1fG5gHZTzvCY9uEGaz25584776hVAaNIt/view?usp=sharing)\
[BitFuSCNN slides](https://drive.google.com/file/d/1kKs1Z09tQxmTDEzF4WKlkY0u9_Zbg7JC/view?usp=sharing)
