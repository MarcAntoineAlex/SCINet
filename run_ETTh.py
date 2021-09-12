import argparse
import os
import torch
import numpy as np
from torch.utils.tensorboard import SummaryWriter
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
from experiments.exp_ETTh import Exp_ETTh

parser = argparse.ArgumentParser(description='[Informer] Long Sequences Forecasting')

parser.add_argument('--model', type=str, required=False, default='SCINet', help='model of the experiment')

parser.add_argument('--data', type=str, required=False, default='ETTh1', help='data')
parser.add_argument('--root_path', type=str, default='./datasets/ETT-data/ETT/', help='root path of the data file')
parser.add_argument('--data_path', type=str, default='ETTh1.csv', help='location of the data file')
parser.add_argument('--features', type=str, default='M', help='features [S, M]')
parser.add_argument('--target', type=str, default='OT', help='target feature')
parser.add_argument('--freq', type=str, default='h', help='freq for time features encoding, options:[s:secondly, t:minutely, h:hourly, d:daily, b:business days, w:weekly, m:monthly], you can also use more detailed freq like 15min or 3h')
parser.add_argument('--checkpoints', type=str, default='./checkpoints/', help='location of model checkpoints')


parser.add_argument('--seq_len', type=int, default=96, help='input sequence length of Informer encoder, look back window')
parser.add_argument('--label_len', type=int, default=48, help='start token length of Informer decoder')
parser.add_argument('--pred_len', type=int, default=48, help='prediction sequence length, horizon')

parser.add_argument('--dropout', type=float, default=0.5, help='dropout')
parser.add_argument('--embed', type=str, default='timeF', help='time features encoding, options:[timeF, fixed, learned]')

parser.add_argument('--do_predict', action='store_true', help='whether to predict unseen future data')
parser.add_argument('--mix', action='store_false', help='use mix attention in generative decoder', default=True)
parser.add_argument('--cols', type=str, nargs='+', help='file list')
parser.add_argument('--num_workers', type=int, default=0, help='data loader num workers')
parser.add_argument('--itr', type=int, default=0, help='experiments times')
parser.add_argument('--train_epochs', type=int, default=100, help='train epochs')
parser.add_argument('--batch_size', type=int, default=32, help='batch size of train input data')
parser.add_argument('--patience', type=int, default=10, help='early stopping patience')
parser.add_argument('--lr', type=float, default=0.0001, help='optimizer learning rate')
parser.add_argument('--des', type=str, default='test',help='exp description')
parser.add_argument('--loss', type=str, default='mae',help='loss function')
parser.add_argument('--lradj', type=str, default='type1',help='adjust learning rate')
parser.add_argument('--use_amp', action='store_true', help='use automatic mixed precision training', default=False)
parser.add_argument('--inverse', type=bool, default =False, help='inverse output data')

parser.add_argument('--use_gpu', type=bool, default=True, help='use gpu')
parser.add_argument('--gpu', type=int, default=0, help='gpu')
parser.add_argument('--use_multi_gpu', action='store_true', help='use multiple gpus', default=False)
parser.add_argument('--devices', type=str, default='0',help='device ids of multile gpus')


parser.add_argument('--share-weight', default=0, type=int, help='share weight or not in attention q,k,v')
parser.add_argument('--temp', default=0, type=int, help='Use temporature weights or not, if false, temp=1')
parser.add_argument('--hidden-size', default=1, type=float, help='hidden channel of module')
parser.add_argument('--INN', default=1, type=int, help='use INN or basic strategy')
parser.add_argument('--kernel', default=5, type=int, help='kernel size, 3, 5, 7')
parser.add_argument('--dilation', default=1, type=int, help='dilation')
parser.add_argument('--window_size', default=12, type=int, help='input size')

parser.add_argument('--single_step', type=int, default=0)
parser.add_argument('--single_step_output_One', type=int, default=0)
parser.add_argument('--lastWeight', type=float, default=1.0)


parser.add_argument('--positionalEcoding', type=bool, default=False)
parser.add_argument('--groups', type=int, default=1)
parser.add_argument('--layers', type=int, default=3)
parser.add_argument('--stacks', type=int, default=1, help='1 stack or 2 stacks')


parser.add_argument('--levels', type=int, default=4,
                    help='# of levels (default: 8)')
parser.add_argument('--nhid', type=int, default=32,
                    help='number of hidden units per layer (default: 30)')
parser.add_argument('--model_name', type=str, default='EncoDeco')
# parser.add_argument('--model_mode', type=str, default='EncoDeco')

parser.add_argument('--concat_len', type=int, default=0)


args = parser.parse_args()

args.use_gpu = True if torch.cuda.is_available() and args.use_gpu else False

if args.use_gpu and args.use_multi_gpu:
    args.devices = args.devices.replace(' ', '')
    device_ids = args.devices.split(',')
    args.device_ids = [int(id_) for id_ in device_ids]
    args.gpu = args.device_ids[0]

data_parser = {
    'ETTh1': {'data': 'ETTh1.csv', 'T': 'OT', 'M': [7, 7, 7], 'S': [1, 1, 1], 'MS': [7, 7, 1]},
    'ETTh2': {'data': 'ETTh2.csv', 'T': 'OT', 'M': [7, 7, 7], 'S': [1, 1, 1], 'MS': [7, 7, 1]},
    'ETTm1': {'data': 'ETTm1.csv', 'T': 'OT', 'M': [7, 7, 7], 'S': [1, 1, 1], 'MS': [7, 7, 1]},
    'ETTm2': {'data': 'ETTm2.csv', 'T': 'OT', 'M': [7, 7, 7], 'S': [1, 1, 1], 'MS': [7, 7, 1]},
    'WTH': {'data': 'WTH.csv', 'T': 'WetBulbCelsius', 'M': [12, 12, 12], 'S': [1, 1, 1], 'MS': [12, 12, 1]},
    'ECL': {'data': 'ECL.csv', 'T': 'MT_320', 'M': [321, 321, 321], 'S': [1, 1, 1], 'MS': [321, 321, 1]},
    'Solar': {'data': 'solar_AL.csv', 'T': 'POWER_136', 'M': [137, 137, 137], 'S': [1, 1, 1], 'MS': [137, 137, 1]},
}
if args.data in data_parser.keys():
    data_info = data_parser[args.data]
    args.data_path = data_info['data']
    args.target = data_info['T']
    args.enc_in, args.dec_in, args.c_out = data_info[args.features]

# args.s_layers = [int(s_l) for s_l in args.s_layers.replace(' ', '').split(',')]
args.detail_freq = args.freq
args.freq = args.freq[-1:]

print('Args in experiment:')
print(args)

torch.manual_seed(4321)  # reproducible
torch.cuda.manual_seed_all(4321)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True  # Can change it to False --> default: False
torch.backends.cudnn.enabled = True

Exp = Exp_ETTh

mae_ = []
maes_ = []
mse_ = []
mses_ = []

if args.itr:
    for ii in range(args.itr):
        # setting record of experiments
        setting = '{}_{}_ft{}_sl{}_ll{}_pl{}_mx{}_{}_lr{}_bs{}_hid{}_s{}_l{}_dp{}_inv{}_itr{}'.format(args.model,args.data, args.features, args.seq_len, args.label_len, args.pred_len,args.mix,args.des,args.learning_rate,args.batch_size,args.hidden_size,args.stacks, args.layers,args.dropout,args.inverse,ii)

        exp = Exp(args)  # set experiments
        print('>>>>>>>start training : {}>>>>>>>>>>>>>>>>>>>>>>>>>>'.format(setting))
        exp.train(setting)

        print('>>>>>>>testing : {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'.format(setting))
        mae, maes, mse, mses = exp.test(setting)
        mae_.append(mae)
        mse_.append(mse)
        maes_.append(maes)
        mses_.append(mses)

        if args.do_predict:
            print('>>>>>>>predicting : {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'.format(setting))
            exp.predict(setting, True)

        torch.cuda.empty_cache()
    print('Final mean normed mse:{:.4f}, std mse:{:.4f}, mae:{:.4f}, std mae:{:.4f}'.format(np.mean(mse_), np.std(mse_), np.mean(mae_),np.std(mae_)))
    print('Final mean denormed mse:{:.4f}, std mse:{:.4f}, mae:{:.4f}, std mae:{:.4f}'.format(np.mean(mses_),np.std(mses_), np.mean(maes_), np.std(maes_)))
    print('Final min normed mse:{:.4f}, mae:{:.4f}'.format(min(mse_), min(mae_)))
    print('Final min denormed mse:{:.4f}, mae:{:.4f}'.format(min(mses_), min(maes_)))
else:
    setting = 'VIS_{}_Levels{}_hid{}_{}_ft{}_sl{}_ll{}_pl{}_mx{}_{}_lr{}_bs{}_hid{}_s{}_l{}_dp{}_inv{}_itr{}'.format(args.model, args.levels, args.nhid, args.data, args.features, args.seq_len, args.label_len, args.pred_len,args.mix,args.des,args.lr,args.batch_size,args.hidden_size,args.stacks, args.layers,args.dropout,args.inverse,args.itr)
    exp = Exp(args)  # set experiments
    print('>>>>>>>start training : {}>>>>>>>>>>>>>>>>>>>>>>>>>>'.format(setting))
    exp.train(setting)

    print('>>>>>>>testing : {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'.format(setting))
    mae, maes, mse, mses = exp.test(setting)
    print('Final mean normed mse:{:.4f},mae:{:.4f},denormed mse:{:.4f},mae:{:.4f}'.format(mse, mae, mses, maes))



