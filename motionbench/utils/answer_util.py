import json

import jsonlines

def polish_answer(answer: str):
    answer = answer.strip()

    answer = answer.split(")")[0]
    answer = answer.strip()

    if "(" in answer:
        try:
            answer = answer.split("(")[1]
            answer = answer.strip()
        except:
            pass

    answer = answer.split(" ")[0]

    if len(answer)>0:
        return answer[0]
    return answer


def get_better_one(answer: str, old_answer: str):
    if old_answer == "":
        return answer

    find_good = False
    for i in range(4):
        option = chr(ord("A") + i)
        if option in old_answer:
            find_good = True
            break
    if not find_good:
        return answer

    return old_answer

def construct_answer(answer_file,final_answer_file):
    final_results = {}
    with jsonlines.open(answer_file) as reader:
        for obj in reader:
            for uid, answer in obj.items():
                if answer is None:
                    answer = ""
                uid = str(uid)
                answer = answer.strip()
                if uid in final_results:
                    answer = get_better_one(answer, final_results[uid])

                final_results[uid] = polish_answer(answer)

    with open(final_answer_file, "w") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=4)