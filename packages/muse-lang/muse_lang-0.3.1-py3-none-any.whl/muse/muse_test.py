import muse.muse_lang as ml
import muse.sample as sample

def test_code(code):
    print(ml.ast_check(code))
    return ml.trial(code)

if __name__ == '__main__':
    result = test_code(sample.demo2)
    if result['code'] == 'SUCCESS':
        print(result['data'])
        print(result['error_msgs'])
    else:
        print(result['error_msgs'])