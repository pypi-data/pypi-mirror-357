# test_cli.py
import fire

def download(url_list: list[str] = []):
    print("sys.argv:", __import__("sys").argv)
    print("url_list:", url_list)

if __name__ == "__main__":
    fire.Fire(download)
