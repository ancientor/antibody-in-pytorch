import numpy as np

from AIPT.Models.Mason2020 import CNN
from AIPT.Models.Mason2020 import LSTM_RNN
from AIPT.Models.Wollacott2019 import Bi_LSTM

def Test_Mason2020_CNN(para_dict, train_loader, test_loader):
    """
    Run the CNN model on OAS dataset
    """
    para_dict['model_name'] = 'CNN_Model'
    para_dict['num_classes'] = len(para_dict['species_type'])
    print('Parameters: ', para_dict)
    model = CNN.CNN_classifier(para_dict)
    model.fit(train_loader)
    output = model.predict(test_loader)
    labels = np.vstack([i for _, i in test_loader])
    model.evaluate(output, labels)

def Test_Mason2020_LSTM_RNN(para_dict, train_loader, test_loader):
    """
    Run the LSTM_RNN model on OAS dataset
    """
    para_dict['model_name'] = 'LSTM_RNN_Model'
    para_dict['num_classes'] = len(para_dict['species_type'])
    print('Parameters: ', para_dict)
    model = LSTM_RNN.LSTM_RNN_classifier(para_dict)
    model.fit(train_loader)
    output = model.predict(test_loader)
    labels = np.vstack([i for _, i in test_loader])
    model.evaluate(output, labels)

def Test_Wollacott2019_Bi_LSTM(para_dict, train_loader, test_loader):
    """
    Run the Bi_LSTM model on OAS dataset
    """
    para_dict['model_name'] = 'Bi_LSTM'
    print('Parameters: ', para_dict)
    model = Bi_LSTM.LSTM_Bi(para_dict)
    model.fit(train_loader)
    # output = model.predict(test_loader)
    # labels = np.vstack([i for _, i in test_loader])
    # model.evaluate(output, labels)
    dict_class = model.roc_plot(test_loader)
    model.plot_score_distribution(dict_class)

