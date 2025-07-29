# zeule/tokenizer.py

def tokenize(text):
    """
    将输入的文本分割成单词列表。
    目前使用简单的空格分割，后续可以扩展为更复杂的分词算法。
    """
    # 去除文本中的标点符号
    punctuation = '.,!?;:"\''
    for char in punctuation:
        text = text.replace(char, "")

    # 使用空格分割文本
    words = text.split()
    return words