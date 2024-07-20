from random import randint
import queue
import cv2
import random
import time
import threading

# import warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="selenium")
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

TANKA_GEN_URL = "https://www.poem-generator.org.uk/tanka/"

class CameraStream:
    def __init__(self):
        self.driver = CameraStream.setup()
        self.capture = cv2.VideoCapture(0)
        self.q = queue.Queue(maxsize=2)  # Limit queue size
        self.stop_event = threading.Event()
        self.text_to_display = "Starting..."
        self.text_lock = threading.Lock()
        self.generate_a_new_poem = False
        self.x, self.y = 50, 50
        self.last_clock = 0 

    def setup():
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-images")

        # Set up the WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Navigate to the tanka generator website
        driver.get(TANKA_GEN_URL)
        return driver

    @staticmethod
    def draw_multiline_text(frame, text, position, font_scale, color, thickness):
        x, y = position
        for line in text.split('\n'):
            cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
            y += int(30 * font_scale)  # Adjust line spacing based on font scale

    def capture_frames(self):
        while not self.stop_event.is_set():
            ret, frame = self.capture.read()
            if not ret:
                break
            with self.text_lock:
                text = self.text_to_display

            self.draw_multiline_text(frame, text, (self.x, self.y), 1.5, (255, 255, 255), 2)
            
            if not self.q.full():
                self.q.put(frame)
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def display_frames(self):
        cv2.namedWindow('Laptop Camera Stream', cv2.WINDOW_NORMAL)
        while not self.stop_event.is_set():
            if not self.q.empty():
                frame = self.q.get()
                try:
                    cv2.imshow('Laptop Camera Stream', frame)
                except cv2.error:
                    print("Error displaying frame")
                    continue
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.stop_event.set()
                elif key == ord(' '):
                    self.text_to_display = "Thinking of a new tanka..."
                    self.last_clock = time.time()
                    self.generate_a_new_poem = True
                    frame_height, frame_width = frame.shape[:2]
                    self.x = random.randint(50, frame_width // 2)  # Adjust based on expected text width
                    self.y = random.randint(50, frame_height // 2)  # Adjust based on expected text height
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def update_text(self):
        while not self.stop_event.is_set() :
            # new_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if self.generate_a_new_poem:
                new_text = self.generate_tanka()
                print("Time spent: " + str(round(time.time() - self.last_clock)) + " seconds")
                print(new_text)
                print()
                with self.text_lock:
                    self.text_to_display = new_text
                time.sleep(2)  # Update text every 2 seconds
                self.generate_a_new_poem = False

    def start(self):
        capture_thread = threading.Thread(target=self.capture_frames)
        text_thread = threading.Thread(target=self.update_text)

        capture_thread.start()
        text_thread.start()

        # Run display_frames in the main thread
        self.display_frames()

        capture_thread.join()
        text_thread.join()
        self.capture.release()
        cv2.destroyAllWindows()

    def generate_tanka(self):
        try:
            # Wait for the generate button to be clickable and click it
            fill_all_button = WebDriverWait(self.driver, 300).until(
                EC.element_to_be_clickable((By.ID, "fill_all"))
            )
            fill_all_button.click()

            self.driver.find_element(By.NAME, 'writer').send_keys('anonymous')
            # Wait for the poem to be generated
            submit_button = WebDriverWait(self.driver, 300).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "create_form_submit"))
            )
            # Click submit button
            submit_button.click()

            poem_element = WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.CLASS_NAME, "poem"))
            )
            # Extract the poem text
            return poem_element.text

        finally:
            time.sleep(1)
            # Close the browser
            self.driver.quit()
            self.driver = CameraStream.setup()
            # self.driver.get(TANKA_GEN_URL)

if __name__ == '__main__':
    stream = CameraStream()
    stream.start()
