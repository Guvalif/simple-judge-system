from pandas import DataFrame, read_csv
from sklearn.metrics import accuracy_score


ANSWER_DF = (read_csv('answer.csv')
    .sort_values(by='index')
    .reset_index(drop=True))


class ValidationError(Exception):
    pass


def validate(df: DataFrame):
    if df.columns != [ 'index', 'class' ]:
        raise ValidationError("列名が 'index' および 'class' ではありません")

    if 'int' not in str(df.dtypes['index']):
        raise ValidationError("'index' 列の値がすべて整数ではありません")


def accuracy(df: DataFrame):
    df = df.sort_values(by='index').reset_index(drop=True)

    if not df['index'].equals(ANSWER_DF['index']):
        raise ValidationError("'index' 列の値が正解データと一致しません")

    return accuracy_score(ANSWER_DF['class'], df['class'])
