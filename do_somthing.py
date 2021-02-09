from utils.file_utils import FileUtils
from utils.general_utils import GeneralUtils
from pandas import DataFrame

df = FileUtils.read_excel_file('resources/persian-swear-words.xlsx')
swear_words = df.iloc[:, 0].tolist()
for w in swear_words:
    for l in w:
        if l not in "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیيى ‌":
            print(w, ',', l)

sorted_lst = [[w, ] for w in GeneralUtils.sort_lis_in_persian(swear_words) ]
FileUtils.write_lists2excel_file(sorted_lst, 'resources/test.xlsx', ['واژه'])
