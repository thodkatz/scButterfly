import getopt
import sys
import gc
import os
from scButterfly.data_processing import RNA_data_preprocessing, ATAC_data_preprocessing
import scanpy as sc
import anndata as ad
from scipy.sparse import csr_matrix
from scButterfly.train_model_perturb import Model
import torch
import torch.nn as nn
from scButterfly.split_datasets import unpaired_split_dataset_perturb


# opts, args = getopt.gnu_getopt(sys.argv[1:], 't:d:f:n', ['model_type=', 'data=', 'file_path=', 'number='])
# model_type = opts[0][1]
# data = opts[1][1]
# file_path = opts[2][1]
# number = opts[3][1]

data = "./data/pbmc/pbmc_perturb.h5ad"
file_path = "./saved_results/butterfly/perturb"
cell_type_indices = [1, 2, 3, 4, 5, 6, 7]
cell_type_index = cell_type_indices[0]
model_type = "basic"

sc_data = sc.read_h5ad(data)
        

############################################################
# Part 1 data processing
RNA_data = sc_data[sc_data.obs.condition == 'control']
RNA_data_stimulated = sc_data[sc_data.obs.condition == 'stimulated']
RNA_data.obs.index = [str(i) for i in range(RNA_data.X.shape[0])]
RNA_data_stimulated.obs.index = [str(i) for i in range(RNA_data_stimulated.X.shape[0])]

############################################################
# Part 2 split datasets
id_list = unpaired_split_dataset_perturb(RNA_data, RNA_data_stimulated)

# To avoid reusing for profiles of stimulated cells, please using the following command
# id_list = unpaired_split_dataset_perturb_no_reusing(RNA_data, ATAC_data)

train_id_r, train_id_a, validation_id_r, validation_id_a, test_id_r, test_id_a = id_list[int(cell_type_index) - 1]



RNA_input_dim = RNA_data.X.shape[1]
RNA_input_stimulated_dim = RNA_data_stimulated.X.shape[1]
assert RNA_input_dim == RNA_input_stimulated_dim # should be pairs, created by optimal transport

R_kl_div = 1 / RNA_input_dim * 20
A_kl_div = 1 / RNA_input_stimulated_dim * 20
kl_div = R_kl_div + A_kl_div

############################################################
# Part 3 construct model
model = Model(
    R_encoder_nlayer = 2, 
    A_encoder_nlayer = 2,
    R_decoder_nlayer = 2, 
    A_decoder_nlayer = 2,
    R_encoder_dim_list = [RNA_input_dim, 256, 128],
    A_encoder_dim_list = [RNA_input_stimulated_dim, 128, 128],
    R_decoder_dim_list = [128, 256, RNA_input_dim],
    A_decoder_dim_list = [128, 128, RNA_input_stimulated_dim],
    R_encoder_act_list = [nn.LeakyReLU(), nn.LeakyReLU()],
    A_encoder_act_list = [nn.LeakyReLU(), nn.LeakyReLU()],
    R_decoder_act_list = [nn.LeakyReLU(), nn.LeakyReLU()],
    A_decoder_act_list = [nn.LeakyReLU(), nn.LeakyReLU()],
    translator_embed_dim = 128, 
    translator_input_dim_r = 128,
    translator_input_dim_a = 128,
    translator_embed_act_list = [nn.LeakyReLU(), nn.LeakyReLU(), nn.LeakyReLU()],
    discriminator_nlayer = 1,
    discriminator_dim_list_R = [128], # how this can be even work? the dim_list + 1 will be out of bounds, should be [128, 1] right? It is handled by the model
    discriminator_dim_list_A = [128],
    discriminator_act_list = [nn.Sigmoid()],
    dropout_rate = 0.1,
    R_noise_rate = 0.5,
    A_noise_rate = 0.5,
    chrom_list = [],
    model_config_log_path = file_path,
    RNA_data = RNA_data,
    ATAC_data = RNA_data_stimulated
)

############################################################
# Part 4 train model

model.train(
    R_encoder_lr = 0.001,
    A_encoder_lr = 0.001,
    R_decoder_lr = 0.001,
    A_decoder_lr = 0.001,
    R_translator_lr = 0.001,
    A_translator_lr = 0.001,
    translator_lr = 0.001,
    discriminator_lr = 0.005,
    R2R_pretrain_epoch = 100,
    A2A_pretrain_epoch = 100,
    lock_encoder_and_decoder = False,
    translator_epoch = 200,
    patience = 50,
    batch_size = 64,
    r_loss = nn.MSELoss(size_average=True),
    a_loss = nn.MSELoss(size_average=True),
    d_loss = nn.BCELoss(size_average=True),
    loss_weight = [1, 1, 1, R_kl_div, A_kl_div, kl_div],
    train_id_r = train_id_r,
    train_id_a = train_id_a,
    validation_id_r = validation_id_r, 
    validation_id_a = validation_id_a, 
    output_path = file_path,
    seed = 19193,
    kl_mean = True,
    R_pretrain_kl_warmup = 50,
    A_pretrain_kl_warmup = 50,
    translation_kl_warmup = 50,
    load_model = None,
    logging_path = file_path
)

############################################################
# Part 5 test model 
model.test(
    test_id_r = test_id_r,
    test_id_a = test_id_a, 
    load_path = file_path,
    load_model = True,
    load_path = file_path,
    test_pca = True,
    test_DEGs = True,
    test_R2 = True,
    test_dotplot = True,
    output_data = False,
    return_predict = False
)
