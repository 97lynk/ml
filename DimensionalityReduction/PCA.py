import pandas as pd

dataset = pd.read_csv('dataset_for_PCA_LDA.csv')
X = dataset.iloc[:, 0:39].values
y = dataset.iloc[:, 39].values

from sklearn.preprocessing import LabelEncoder
lb_enc = LabelEncoder()
lb_enc.fit(y)
y = lb_enc.transform(y)

from sklearn.preprocessing import StandardScaler
X_std = StandardScaler().fit_transform(X)

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_std, y, test_size=0.2, random_state=0)
clf = LogisticRegression(solver='lbfgs')
clf.fit(X_train, y_train)
y_predict = clf.predict(X_test)

target_names = ['%s' % i for i in lb_enc.classes_]
actual_names = ['actual %s' % i for i in lb_enc.classes_]
predict_names = ['predicted %s' % i for i in lb_enc.classes_]
y_test_report, y_predict_report = lb_enc.inverse_transform(y_test), lb_enc.inverse_transform(y_predict)

from sklearn.metrics import confusion_matrix, classification_report
conf_1 = confusion_matrix(y_test_report, y_predict_report, target_names)
table_conf_1 = pd.DataFrame(conf_1, actual_names, predict_names)
report_1 = classification_report(y_test_report, y_predict_report, target_names)
print('Using Logistic Regression before apply PCA')
print('===================Confusion Matrix 1==================\n%s' % table_conf_1)
print('===================Report 1============================\n%s' % report_1)

import numpy as np

cov_mat = np.cov(X_std.T)
print('Covariance matrix: \n%s' % cov_mat)
cor_mat = np.corrcoef(X_std.T)
print('Correlation matrix: \n%s' % cor_mat)

eig_vals, eig_vecs = np.linalg.eig(cor_mat)
eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:, i]) for i in range(len(eig_vals))]
eig_pairs.sort()
eig_pairs.reverse()
print('Eigenvalues in descending order:')
for value in eig_pairs:
    print(value[0])

tot = sum(eig_vals)
var_exp = [(i / tot) * 100 for i in sorted(eig_vals, reverse=True)]
x_pos = ['PC %s' % i for i in np.arange(len(var_exp))]

for index, pc in enumerate(x_pos):
    print('%s = %.2f%%' % (pc, var_exp[index]))

import matplotlib.pyplot as plt

# lấy 3 PC đầu
var_exp = var_exp[0:3]
x_pos = x_pos[0:3]
cum_var_exp = np.cumsum(var_exp)

plt.figure(1, figsize=(6, 4))
plt.plot(cum_var_exp, color='green')
# nối các chấm trên
plt.scatter(x_pos, cum_var_exp, color='orange', label='cumulative explained variance')
# vẽ các bar với giá trị là explained variance
bars = plt.bar(x_pos, var_exp, align='center', alpha=0.5, label='individual explained variance')

# thêm text cho bar
for index, bar in enumerate(bars):
    plt.text(bar.get_x() + .2, bar.get_height() - 5, '{:.2f}%'.format(var_exp[index]), fontsize=18, color='blue')

# thêm text cho chấm
for i, value in enumerate(cum_var_exp):
    plt.text(x_pos[i], cum_var_exp[i] + 2, '{:.2f}%'.format(value))

plt.xticks(x_pos)
plt.ylabel('Explained variance ratio')
plt.xlabel('Principal components')
plt.title('Explained variance by different principal components')
plt.legend(loc='best')
plt.tight_layout()
# plt.show()

matrix_w = np.hstack((eig_pairs[0][1].reshape(X.shape[1], 1),
                      eig_pairs[1][1].reshape(X.shape[1], 1),
                      eig_pairs[2][1].reshape(X.shape[1], 1)))

X_new = X_std.dot(matrix_w)

from sklearn.decomposition import PCA

pca = PCA(n_components=3)
X_new = pca.fit_transform(X_std)
matrix_w = pca.components_.T

X_train, X_test = X_train.dot(matrix_w), X_test.dot(matrix_w)

clf = LogisticRegression(solver='lbfgs')
clf.fit(X_train, y_train)
y_predict = clf.predict(X_test)
y_predict_report = lb_enc.inverse_transform(y_predict)

conf_2 = confusion_matrix(y_test_report, y_predict_report, target_names)
table_conf_2 = pd.DataFrame(conf_2, actual_names, predict_names)
report_2 = classification_report(y_test_report, y_predict_report, target_names)
print('Using Logistic Regression after apply PCA with n=3')
print('===================Confusion Matrix 2==================\n%s' % table_conf_2)
print('===================Report 2============================\n%s' % report_2)

from mpl_toolkits.mplot3d import Axes3D

plt.figure(2)
colors = {
    0: 'red',  # NO label
    1: 'green'
}
ax = plt.subplot(111, projection='3d')
for index, val in enumerate(X_new):
    xdata = val[0]
    ydata = val[1]
    zdata = val[2]
    ax.scatter(xdata, ydata, zdata, color=colors.get(y[index]))
ax.set_xlabel('Principal Component 1')
ax.set_ylabel('Principal Component 2')
ax.set_zlabel('Principal Component 3')
