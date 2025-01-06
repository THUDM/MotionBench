import json
import jsonlines
from collections import defaultdict


def compute_accuracy(answer_file: str, video_meta_file: str):
    total_qa_num = 0
    total_answered_num = 0
    right_num = 0

    category_right = defaultdict(float)
    category_total = defaultdict(float)
    category_acc = defaultdict(float)

    with open(answer_file) as f:
        model_answers = json.load(f)

    with jsonlines.open(video_meta_file) as reader:
        video_meta = list(reader)
        for meta_data in video_meta:
            for qa in meta_data['qa']:
                uid = str(qa["uid"])
                if uid in model_answers:
                    total_answered_num += 1
                    model_answer = model_answers[uid]
                    # if "question_type" in qa:
                    # for category in qa['question_type']:
                    meta_data['question_type'] = [meta_data['question_type']]
                    if qa["answer"] == "NA":
                        continue
                    for category in meta_data['question_type']:
                        category_total[category] += 1
                        if model_answer == qa["answer"]:
                            category_right[category] += 1

                    if model_answer == qa["answer"]:
                        right_num += 1
                total_qa_num += 1

    for key in category_total:
        category_acc[key] = category_right[key] / category_total[key]

    acc = float(right_num) / total_qa_num
    answered_acc = float(right_num) / total_answered_num
    category_acc.update({"acc": acc, "answered_acc": answered_acc, "total_qa_num": total_qa_num,
                         "total_answered_num": total_answered_num, "right_num": right_num})
    return category_acc


