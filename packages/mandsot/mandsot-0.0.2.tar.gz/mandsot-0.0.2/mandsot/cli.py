import sys, os
import argparse
from mandsot import features, dataloader, model, train, eval
import torch
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mode", "--mode", type=str, required=True, choices=['train', 'infer', 'vis'], help="")
    parser.add_argument("-model", "--model", type=str, required=False, help="model for training/prediction")
    parser.add_argument("-mc", "--model_class", type=str, required=False, default='transformer', choices=['cnn', 'rnn', 'transformer'], help="type of model")
    parser.add_argument("-device", "--device", type=str, required=False, default='auto', choices=['cuda', 'mps', 'cpu', 'auto'], help="")
    parser.add_argument("-seed", "--seed", type=int, required=False, default=42, help="random seed for dataset shuffling")
    parser.add_argument("-rt", "--max_rt", type=float, required=False, default=1500, help="maximum reaction time to be included in the training dataset - in ms")
    parser.add_argument("-noise", "--static_noise", type=bool, required=False, default=False, help="")
    parser.add_argument("-noise_width", "--static_noise_width", type=float, required=False, default=0.5, help="window length of static noise")
    parser.add_argument("-w1", "--w1", type=float, required=False, default=1, help="")
    parser.add_argument("-w2", "--w2", type=float, required=False, default=0, help="")
    parser.add_argument("-w3", "--w3", type=float, required=False, default=1, help="")
    parser.add_argument("-audio", "--audio", type=str, required=False, help="")
    parser.add_argument("-audio_dir", "--audio_dir", type=str, required=False, help="")
    parser.add_argument("-csv", "--csv", type=str, required=False, help="")
    parser.add_argument("-enc", "--csv_encoding", type=str, required=False, default="utf-8", help="")
    parser.add_argument("-test", "--test_ratio", type=float, required=False, default=0.2, help="")
    parser.add_argument("-esp", "--earlystop_patience", type=int, required=False, default=5, help="")
    parser.add_argument("-esd", "--earlystop_delta", type=float, required=False, default=0, help="")
    parser.add_argument("-batch", "--batch_size", type=int, required=False, default=64, help="")
    parser.add_argument("-keep", "--keep_all", type=bool, required=False, default=True, help="")
    parser.add_argument("-o", "--output", type=str, required=False, help="")
    parser.add_argument("-cont", "--continued_train", type=bool, required=False, help="")
    parser.add_argument("-lr", "--learning_rate", type=float, required=False, default=0.001, help="")
    parser.add_argument("-verbose", "--verbose", type=bool, required=False, default=True, help="")
    args = parser.parse_args()

    if args.mode == 'train':
        # prepare dataset
        if args.csv is not None:
            dataset = dataloader.load_train_csv(args.csv, args.verbose)
        elif args.audio_dir is not None:
            dataset = dataloader.load_data_from_subject_csv(args.audio_dir, os.path.join(args.output, 'train_data.csv'), args.max_rt, args.csv_encoding, args.verbose)
        else:
            print("Error: You must specify the labeled data for training with either --csv or --audio_dir.")
            sys.exit(1)
        dataset = dataloader.load_features(dataset, args.static_noise, args.static_noise_width, args.w1, args.w2, args.w3, args.verbose)
        dataset_train, dataset_test = dataloader.split_dataset(dataset, test_ratio=args.test_ratio, random_state=args.seed)

        # load dataset for training
        batch_size = args.batch_size
        dataset_train = dataloader.VoiceDataset(dataset_train)
        dataset_test = dataloader.VoiceDataset(dataset_test)
        train_loader = dataloader.load_dataset(dataset_train, batch_size=batch_size, shuffle=True)
        test_loader = dataloader.load_dataset(dataset_test, batch_size=batch_size, shuffle=False)

        # config train parameters
        if args.device != 'auto':
            device = torch.device(args.device)
        else:
            device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        early_stopping = train.EarlyStopping(patience=args.earlystop_patience, delta=args.earlystop_delta)

        # load model
        if args.continued_train:
            if args.model is None:
                print("Error: You must specify a model path with --model when using --continued_train.")
                sys.exit(1)
            else:
                if args.model_class == 'cnn':
                    sot_model = model.load_model(model.MandSOT, args.model, device, args.verbose)
                elif args.model_class == 'rnn':
                    sot_model = model.load_model(model.MandSOTRNN, args.model, device, args.verbose)
                else:
                    sot_model = model.load_model(model.MandSOTTransformer, args.model, device, args.verbose)
        else:
            if args.model_class == 'cnn':
                sot_model = model.MandSOT().to(device)
            elif args.model_class == 'rnn':
                sot_model = model.MandSOTRNN().to(device)
            else:
                sot_model = model.MandSOTTransformer().to(device)

        # start training
        train.start(sot_model, train_loader, test_loader, device, args.learning_rate, early_stopping, args.output, args.keep_all)
    elif args.mode == 'infer':
        batch_size = args.batch_size

        # prepare dataset
        if args.csv is not None:
            dataset = dataloader.load_pred_csv(args.csv, args.verbose)
        elif args.audio_dir is not None:
            dataset = dataloader.load_pred_from_dir(args.audio_dir, args.verbose)
        elif args.audio is not None:
            dataset = dataloader.load_single_wav(args.audio, args.verbose)
            batch_size = 1
        else:
            print("Error: You must specify audio paths with --csv, --audio_dir or --audio.")
            sys.exit(1)
        # extract features
        dataset = dataloader.load_features(dataset, args.static_noise, args.static_noise_width, args.w1, args.w2, args.w3, args.verbose)

        # load dataset for prediction
        dataset = dataloader.PredictionDataset(dataset)
        pred_loader = dataloader.load_dataset(dataset, batch_size=batch_size, shuffle=False)

        # config train parameters
        if args.device != 'auto':
            device = torch.device(args.device)
        else:
            device = torch.device(
                "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

        # load model
        if args.model_class == 'cnn':
            sot_model = model.load_model(model.MandSOT, args.model, device, args.verbose)
        elif args.model_class == 'rnn':
            sot_model = model.load_model(model.MandSOTRNN, args.model, device, args.verbose)
        else:
            sot_model = model.load_model(model.MandSOTTransformer, args.model, device, args.verbose)

        # infer
        pred = eval.predict(sot_model, pred_loader, device)
        print(pred)
        pred.to_csv("prediction_results.csv", index=False)

    else:  # args.mode == 'vis'
        features.view_features(args.audio, args.static_noise, args.static_noise_width, args.w1, args.w2, args.w3)
