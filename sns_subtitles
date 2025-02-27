from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import pandas as pd
import subprocess
import openai
import requests
import json
from bs4 import BeautifulSoup
import datetime
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pydub import AudioSegment
import threading

# API 키 및 설정
openai.api_key = 'api_key'
OUTPUT_DIR = '경로 지정'
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "progress_log.txt")

def log_progress(message):
    """ 로그 기록 함수 """
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(f"{datetime.datetime.now()}: {message}\n")
    print(message)

def safe_remove(file_path):
    """ 안전한 파일 삭제 함수 """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        log_progress(f"❌ 파일 삭제 실패: {file_path} - {e}")

def get_instagram_post_text(url):
    """ 인스타그램 게시글에서 텍스트 추출 """
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find('meta', property='og:description')
        return meta_tag['content'] if meta_tag else "No text found"
    except requests.RequestException as e:
        log_progress(f"❌ Instagram 텍스트 추출 실패: {url} - {e}")
        return "Failed to retrieve"

def split_audio(audio_path, chunk_length_ms=60000):
    """ 오디오 파일을 chunk_length_ms(기본 60초) 단위로 나눠서 리스트 반환 """
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_ms):
        chunk_path = f"{audio_path}_part{i//chunk_length_ms}.wav"
        chunk = audio[i:i+chunk_length_ms]
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks

def transcribe_audio_with_openai(audio_chunk):
    """ 오디오를 Whisper API에 전송하여 변환 (멀티스레딩 적용) """
    try:
        with open(audio_chunk, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
        return response.get("text", "")
    except Exception as e:
        log_progress(f"❌ Whisper 변환 실패: {audio_chunk} - {e}")
        return ""

def process_url(url, index):
    """ URL을 받아서 비디오 다운로드 → 오디오 변환 → Whisper 변환 """
    start_time = time.time()  # 시작 시간 기록
    thread_name = threading.current_thread().name  # 현재 실행 중인 스레드 이름
    log_progress(f"🚀 [{thread_name}] {index}번 URL 처리 시작: {url}")

    unique_id = f"url_{index}"
    video_file = os.path.join(OUTPUT_DIR, f"{unique_id}_video.mp4")
    audio_file = os.path.join(OUTPUT_DIR, f"{unique_id}_audio.wav")

    post_text = get_instagram_post_text(url)
    whisper_text = ""

    try:
        # 비디오 다운로드
        metadata = subprocess.run(['yt-dlp', '--dump-json', url], check=True, capture_output=True, text=True).stdout
        if 'duration' in metadata:
            subprocess.run(['yt-dlp', '-o', video_file, url], check=True)
            
            # 비디오에서 오디오 추출
            AudioFileClip(video_file).write_audiofile(audio_file)

            # 오디오 분할
            audio_chunks = split_audio(audio_file)

            # 멀티스레딩으로 Whisper 변환 실행
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(transcribe_audio_with_openai, chunk): chunk for chunk in audio_chunks}
                for future in as_completed(futures):
                    whisper_text += future.result() + " "

    except Exception as e:
        log_progress(f"❌ [{thread_name}] URL 처리 실패: {url} - {e}")
    finally:
        safe_remove(video_file)
        safe_remove(audio_file)

    elapsed_time = time.time() - start_time  # 실행 시간 계산
    log_progress(f"✅ [{thread_name}] {index}번 URL 처리 완료 (⏱ {elapsed_time:.2f}초)")
    return index, post_text, whisper_text.strip()

def main():
    start_time = time.time()
    
    df = target  # 처리할 대상 데이터 (DataFrame)
    results = []

    # URL 단위로 멀티스레딩 실행
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_url, row['url'], i): i for i, row in df.iterrows()}
        
        for future in as_completed(futures):
            results.append(future.result())

    # DataFrame에 결과 저장
    for index, post_text, whisper_text in results:
        df.at[index, 'whisper_text'] = whisper_text
        df.at[index, 'post'] = post_text

    output_file = os.path.join(OUTPUT_DIR, "파일이름지정_{datetime.datetime.now():%y%m%d}.xlsx")
    df.to_excel(output_file, index=False)
    
    elapsed_time = time.time() - start_time
    log_progress(f"✅ 총 {len(df)}건 처리 완료. 소요 시간: {elapsed_time:.2f}초")
    log_progress(f"🎯 결과 파일 저장 완료: {output_file}")

if __name__ == "__main__":
    main()
