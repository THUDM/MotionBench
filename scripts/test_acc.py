import json

from motionbench.metrics.compute_accuracy import compute_accuracy


def main():
    result = compute_accuracy("random_answers.json", "/workspace/chengyean/motionbench_release/flixdetailbench/data/all_ans_video_info.meta.jsonl")
    print(result)

    with open("result.json",'w') as f:
        json.dump(result, f, indent=4)
        print(f"result.json generated! You can submit your results to https://huggingface.co/spaces/THUDM/TOBEADD")




if __name__ == '__main__':
    main()
