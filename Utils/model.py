import torch
import torch.nn as nn
import torch.optim as optim
from . import loader
import os, json
import numpy as np
from sklearn.metrics import confusion_matrix, matthews_corrcoef, accuracy_score


class Model(nn.Module):

    def __init__(self, para_dict, *args, **kwargs):
        super(Model, self).__init__()

        self.para_dict = para_dict
        self.workpath = os.path.join(os.getcwd(), 'work')

        if 'model_name' not in para_dict:
            self.model_name = 'Model'
        else:
            self.model_name = self.para_dict['model_name']
        if 'seq_len' not in para_dict:
            self.seq_len = 10
        else:
            self.seq_len = self.para_dict['seq_len']
        if 'epoch' not in para_dict:
            self.epoch = 50
        else:
            self.epoch = self.para_dict['epoch']
        if 'batch_size' not in para_dict:
            self.batch_size = 20
        else:
            self.batch_size = self.para_dict['batch_size']
        if 'step_size' not in para_dict:
            self.step_size = 5
        else:
            self.step_size = self.para_dict['step_size']
        if 'learning_rate' not in para_dict:
            self.learning_rate = 0.01
        else:
            self.learning_rate = self.para_dict['learning_rate']
        if 'optim_name' not in para_dict:
            self.optim_name = 'Adam'
        else:
            self.optim_name = self.para_dict['optim_name']

        self.modelnamepath = os.path.join(self.workpath, self.model_name)
        self.modelpath = os.path.join(self.modelnamepath, 'model')

        if not os.path.exists(self.workpath):
            os.mkdir(self.workpath)
        if not os.path.exists(self.modelnamepath):
            os.mkdir(self.modelnamepath)

    def net_init(self):

        self.fc = nn.Linear(20 * self.seq_len, 2)

    def forward(self, x):

        x = x.view(x.shape[0], 20 * self.seq_len)
        x = self.fc(x)
        x = torch.sigmoid(x)

        return x

    def objective(self):
        return nn.CrossEntropyLoss()

    def optimizers(self):

        if self.optim_name == 'Adam':
            return optim.Adam(self.parameters(), lr=self.learning_rate)

        elif self.optim_name == 'RMSprop':
            return optim.RMSprop(self.parameters(), lr=self.learning_rate)

        elif self.optim_name == 'SGD':
            return optim.SGD(self.parameters(), lr=self.learning_rate)

    def fit(self, train_loader):

        self.net_init()
        saved_epoch = self.load_model()

        self.train()
        optimizer = self.optimizers()
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=self.step_size, gamma=0.5 ** (self.epoch / self.step_size))
        total_loss = i = 0
        for e in range(saved_epoch, self.epoch):
            for features, labels in train_loader:
                outputs_train = []
                logps = self.forward(features)
                loss = self.objective()
                loss = loss(logps, labels.type(torch.long))
                total_loss += loss
                i += 1
                outputs_train.append(logps.detach().numpy())
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                scheduler.step()

            self.save_model('Epoch_' + str(e + 1), self.state_dict())
            print('Epoch: %d: Loss=%.3f' % (e + 1, total_loss / i))

    def predict(self, test_loader):

        self.eval()
        test_loss = 0
        outputs_test = []
        labels_test = []
        with torch.no_grad():
            for data_1 in test_loader:
                inputs, labels = data_1
                outputs = self.forward(inputs)
                batch_loss = self.objective()
                batch_loss = batch_loss(outputs, labels.type(torch.long))
                test_loss += batch_loss.item()
                outputs_test.append(outputs.detach().numpy())
                labels_test.append(labels)

            return outputs_test, labels_test

    def evaluate(self, outputs, labels):

        y_pred = []
        for a in outputs:
            y_pred.append(a[0][1] / (a[0][1] + a[0][0]))
        y_true = np.array(labels)
        y_pred = np.array(y_pred).round()
        mat = confusion_matrix(y_true, y_pred)
        acc = accuracy_score(y_true, y_pred)
        mcc = matthews_corrcoef(y_true, y_pred)

        print('Test: ')
        print(mat)
        print('Accuracy = %.3f ,MCC = %.3f' % (acc, mcc))

        return mat, acc, mcc

    def save_model(self, filename, model):

        if not os.path.exists(self.modelpath):
            os.mkdir(self.modelpath)
            torch.save(model, os.path.join(self.modelpath, filename))
        else:
            torch.save(model, os.path.join(self.modelpath, filename))

    def load_model(self):

        for e in range(self.epoch, 0, -1):
            if os.path.isfile(os.path.join(self.modelpath, 'Epoch_' + str(e))):
                print(os.path.join(self.modelpath, 'Epoch_' + str(e)))
                self.load_state_dict(torch.load(os.path.join(self.modelpath, 'Epoch_' + str(e))))
                return e
        return 0

    def save_param(self, path, para_dict):
        with open(os.path.join(path, 'train_parameters.json'), 'w') as f:
            json.dump(para_dict, f, indent=2)

    def load_param(self, path):
        if os.path.exists(os.path.join(path, 'train_parameters.json')):
            return json.load(open(os.path.join(path, 'train_parameters.json'), 'r'))
        return None


if __name__ == '__main__':

    para_dict = {'num_samples': 1000,
                 'seq_len': 20,
                 'batch_size': 20,
                 'model_name': 'Model',
                 'optim_name': 'Adam',
                 'step_size': 10,
                 'epoch': 25,
                 'learning_rate': 0.01}

    data, out = loader.synthetic_data(num_samples=para_dict['num_samples'], seq_len=para_dict['seq_len'])
    data = loader.encode_data(data)
    train_loader, test_loader = loader.train_test_loader(data, out, test_size=0.3, batch_size=20)
    model = Model(para_dict)

    if model.load_param(model.modelnamepath) is None:
        model.save_param(model.modelnamepath, model.para_dict)
    model.fit(train_loader)

    out_test, labels_test = model.predict(test_loader)
    mat, acc, mcc = model.evaluate(out_test, labels_test)
