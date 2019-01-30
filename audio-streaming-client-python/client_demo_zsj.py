# -*-coding:utf-8-*-
import threading
from baidu_acu_asr.asr_client import AsrClient
import os
import time
import logging
import threadpool


class AudioHandler:

    def __init__(self):
        pass

    logging.basicConfig(filename="asr_result.log")
    url = "172.18.53.12"
    port = "8200"
    log_level = 0
    product_id = "1906"
    enable_flush_data = False

    def write_file(self, file_path, file_content):
        with open(file_path, "w") as file:
            file.write(file_content.encode("UTF-8"))

    def get_audio_files(self, path):
        audio_names = os.listdir(path)
        audio_paths = []
        for audio_name in audio_names:
            if audio_name.endswith(".wav") or audio_name.endswith(".pcm"):
                logging.info(os.path.join(path, audio_name))
                audio_paths.append(os.path.join(path, audio_name))
        return audio_paths

    def run(self, file_path):
        while True:
            client = AsrClient(self.url, self.port, self.product_id, self.enable_flush_data,
                               log_level=self.log_level, send_per_seconds= 0.01)
            responses = client.get_result(file_path)
            file_content = ""
            try:
                for response in responses:
                    file_content += response.result
                    logging.info(file_content)
                self.write_file(file_path + ".txt", file_content)
                logging.info("file %s write complete!", file_path)
                break
            except:
                # 如果出现异常，此处需要重试当前音频
                logging.error("connect to server error, will create a new channel and retry audio!")
                time.sleep(0.5)


if __name__ == '__main__':
    start_time = time.time()
    handler = AudioHandler()

    audio_path = "/home/luoyl001/PycharmProjects/baidu_asr/new_wav_8k"
    audio_files = handler.get_audio_files(audio_path)
    pool = threadpool.ThreadPool(10)
    requests = threadpool.makeRequests(handler.run, audio_files)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    logging.info("complete! use time: %s", str(time.time() - start_time))
