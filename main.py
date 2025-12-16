from ursina import *
from ursina.prefabs.health_bar import HealthBar
import random
import math
import csv
import os
import cv2
import mediapipe as mp
import threading
HIGHSCORE_FILE = 'highscores.csv'
def load_highscores():
    scores = []
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        name = row[0]
                        score = int(row[1])
                        scores.append({'name': name, 'score': score})
        scores.sort(key=lambda x: x['score'], reverse=True)
        scores = scores[:10]
    except Exception as e:
        print(f"Error loading highscores: {e}")
        scores = []
    return scores
def save_highscore(name, score):
    scores = load_highscores()
    scores.append({'name': name, 'score': score})
    scores.sort(key=lambda x: x['score'], reverse=True)
    scores = scores[:10]  
    try:
        with open(HIGHSCORE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            for s in scores:
                writer.writerow([s['name'], s['score']])
    except Exception as e:
        print(f"Error saving highscore: {e}")
def is_highscore(score):
    scores = load_highscores()
    if len(scores) < 10:
        return True
    return score > scores[-1]['score']
app = Ursina()

camera_status_text = Text(text='[CAMERA ACTIVE]', position=(0.7, 0.45), scale=1, color=color.red, enabled=False)


class MenuState:
    MAIN_MENU = 'main_menu'
    PLAYING = 'playing'
    GAME_OVER = 'game_over'
    HIGH_SCORES = 'high_scores'
    ENTER_NAME = 'enter_name'
current_menu_state = MenuState.MAIN_MENU
main_menu = Entity(parent=camera.ui, enabled=True)
Entity(
    parent=main_menu,
    model='quad',
    color=color.rgb32(20, 20, 40),
    scale=(2, 1.5)
)
Text(
    parent=main_menu,
    text='HIGHWAY',
    position=(0, 0.35),
    origin=(0, 0),
    scale=5,
    color=color.yellow
)
Text(
    parent=main_menu,
    text='STAMPEDE',
    position=(0, 0.22),
    origin=(0, 0),
    scale=4,
    color=color.orange
)
Text(
    parent=main_menu,
    text='Lasso cars like a cowboy!',
    position=(0, 0.1),
    origin=(0, 0),
    scale=1.5,
    color=color.white
)
play_button = Button(
    parent=main_menu,
    text='PLAY',
    color=color.green,
    highlight_color=color.lime,
    scale=(0.3, 0.08),
    position=(0, -0.05),
    text_color=color.white
)
highscore_button = Button(
    parent=main_menu,
    text='HIGH SCORES',
    color=color.azure,
    highlight_color=color.cyan,
    scale=(0.3, 0.08),
    position=(0, -0.17),
    text_color=color.white
)
quit_button = Button(
    parent=main_menu,
    text='QUIT',
    color=color.red,
    highlight_color=color.orange,
    scale=(0.3, 0.08),
    position=(0, -0.29),
    text_color=color.white
)
Text(
    parent=main_menu,
    text='[A/D] Steer | [SPACE] Jump & Lasso',
    position=(0, -0.42),
    origin=(0, 0),
    scale=1.2,
    color=color.gray
)
highscore_panel = Entity(parent=camera.ui, enabled=False)
Entity(
    parent=highscore_panel,
    model='quad',
    color=color.rgb32(20, 20, 50),
    scale=(1.2, 1.2)
)
Text(
    parent=highscore_panel,
    text='HIGH SCORES',
    position=(0, 0.45),
    origin=(0, 0),
    scale=3,
    color=color.yellow
)
highscore_texts = []
for i in range(10):
    t = Text(
        parent=highscore_panel,
        text='',
        position=(0, 0.3 - i * 0.065),
        origin=(0, 0),
        scale=1.5,
        color=color.white
    )
    highscore_texts.append(t)
back_button = Button(
    parent=highscore_panel,
    text='BACK',
    color=color.orange,
    highlight_color=color.yellow,
    scale=(0.25, 0.07),
    position=(0, -0.45),
    text_color=color.white
)
name_entry_panel = Entity(parent=camera.ui, enabled=False)
Entity(
    parent=name_entry_panel,
    model='quad',
    color=color.rgba32(0, 0, 0, 220),
    scale=(1.2, 0.65)
)
Text(
    parent=name_entry_panel,
    text='NEW HIGH SCORE!',
    position=(0, 0.2),
    origin=(0, 0),
    scale=3,
    color=color.yellow
)
name_entry_score_text = Text(
    parent=name_entry_panel,
    text='Score: 0',
    position=(0, 0.1),
    origin=(0, 0),
    scale=2,
    color=color.lime
)
Text(
    parent=name_entry_panel,
    text='Enter your name:',
    position=(0, 0.0),
    origin=(0, 0),
    scale=1.5,
    color=color.white
)
player_name_text = Text(
    parent=name_entry_panel,
    text='_',
    position=(0, -0.1),
    origin=(0, 0),
    scale=2.5,
    color=color.cyan
)
Text(
    parent=name_entry_panel,
    text='Type your name, then press ENTER',
    position=(0, -0.22),
    origin=(0, 0),
    scale=1.2,
    color=color.gray
)
player_name_input = ""
window.title = 'Highway Stampede'
window.borderless = False
SKY_COLOR = color.rgb32(110, 190, 255) 
window.color = SKY_COLOR
scene.fog_color = SKY_COLOR
scene.fog_density = 0.005
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))
sun.color = color.rgb32(255, 255, 240)
sun.shadows = True
VEHICLE_CONFIGS = {
    'sedan': {
        'model': 'assets/sedan.obj',
        'wheel': 'assets/wheel-default.obj',
        'speed': 22,
        'wild_time': 8.0,
        'points': 100,
        'col': color.red,
        'scale': 1.5,
        'wheel_scale': 0.4,
        'wheel_positions': [(-0.55, 0.2, 0.75), (0.55, 0.2, 0.75), (-0.55, 0.2, -0.65), (0.55, 0.2, -0.65)]
    },
    'taxi': {
        'model': 'assets/taxi.obj',
        'wheel': 'assets/wheel-default.obj',
        'speed': 25,
        'wild_time': 6.0,
        'points': 150,
        'col': color.yellow,
        'scale': 1.5,
        'wheel_scale': 0.4,
        'wheel_positions': [(-0.55, 0.2, 0.75), (0.55, 0.2, 0.75), (-0.55, 0.2, -0.65), (0.55, 0.2, -0.65)]
    },
    'suv': {
        'model': 'assets/suv.obj',
        'wheel': 'assets/wheel-default.obj',
        'speed': 20,
        'wild_time': 9.0,
        'points': 120,
        'col': color.blue,
        'scale': 1.5,
        'wheel_scale': 0.45,
        'wheel_positions': [(-0.6, 0.25, 0.85), (0.6, 0.25, 0.85), (-0.6, 0.25, -0.75), (0.6, 0.25, -0.75)]
    },
    'ambulance': {
        'model': 'assets/ambulance.obj',
        'wheel': 'assets/wheel-truck.obj',
        'speed': 18,
        'wild_time': 12.0,
        'points': 250,
        'col': color.white,
        'scale': 1.6,
        'wheel_scale': 0.5,
        'wheel_positions': [(-0.65, 0.3, 1.0), (0.65, 0.3, 1.0), (-0.65, 0.3, -0.9), (0.65, 0.3, -0.9)]
    },
    'race': {
        'model': 'assets/race.obj',
        'wheel': 'assets/wheel-default.obj',
        'speed': 30,
        'wild_time': 4.0,
        'points': 400,
        'col': color.orange,
        'scale': 1.5,
        'wheel_scale': 0.35,
        'wheel_positions': [(-0.5, 0.18, 0.7), (0.5, 0.18, 0.7), (-0.5, 0.18, -0.6), (0.5, 0.18, -0.6)]
    },
    'van': {
        'model': 'assets/van.obj',
        'wheel': 'assets/wheel-truck.obj',
        'speed': 19,
        'wild_time': 10.0,
        'points': 130,
        'col': color.violet,
        'scale': 1.6,
        'wheel_scale': 0.5,
        'wheel_positions': [(-0.65, 0.3, 1.1), (0.65, 0.3, 1.1), (-0.65, 0.3, -1.0), (0.65, 0.3, -1.0)]
    },
    'police': {
        'model': 'assets/sedan.obj',
        'wheel': 'assets/wheel-default.obj',
        'speed': 32,  
        'wild_time': 2.5,  
        'points': 500,  
        'col': color.rgb32(0, 50, 200),
        'scale': 1.5,
        'wheel_scale': 0.4,
        'wheel_positions': [(-0.55, 0.2, 0.75), (0.55, 0.2, 0.75), (-0.55, 0.2, -0.65), (0.55, 0.2, -0.65)],
        'is_police': True  
    },
}
COLORMAP_TEXTURE = 'assets/colormap.png'
LEFT_BOUND = -10
RIGHT_BOUND = 10
class GameState:
    def __init__(self):
        self.reset()
    def reset(self):
        self.score = 0
        self.combo = 1
        self.max_combo = 1
        self.game_over = False
        self.world_speed = 25
state = GameState()

class HeadTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.head_tilt = 0.0
        self.running = False
        self.thread = None
        self.deadzone = 0.08
        self.sensitivity = 4.0
        
    def start(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Warning: Could not open camera")
            return
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
    def _update_loop(self):
        while self.running:
            if not self.cap or not self.cap.isOpened():
                continue
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                camera_status_text.text = "Face Connected"
                camera_status_text.color = color.green
                landmarks = results.multi_face_landmarks[0].landmark
                left_face = landmarks[234]
                right_face = landmarks[454]
                nose = landmarks[1]
                face_center_x = (left_face.x + right_face.x) / 2
                offset = (nose.x - face_center_x) * self.sensitivity
                
                if abs(offset) < self.deadzone:
                    self.head_tilt = 0
                else:
                    self.head_tilt = max(-1.0, min(1.0, offset))
            else:
                camera_status_text.text = "No Face Detected"
                camera_status_text.color = color.red
                self.head_tilt *= 0.8
            cv2.waitKey(1)
    
    def get_tilt(self):
        return self.head_tilt

head_tracker = HeadTracker()

def distance_2d(e1, e2):
    dx = e1.x - e2.x
    dz = e1.z - e2.z
    return math.sqrt(dx*dx + dz*dz)
class Ground(Entity):
    def __init__(self):
        super().__init__()
        self.segments = []
        for i in range(6):
            seg = Entity(
                model='cube',
                scale=(60, 1, 60),
                color=color.rgb32(139, 90, 60),
                position=(0, -1, i * 60 - 60),
                texture='white_cube',
                transparency=1
            )
            road = Entity(
                parent=seg,
                model='cube',
                scale=(0.4, 1.02, 1),
                color=color.black,
                texture='white_cube',
                position=(0, 0.01, 0)
            )
            Entity(
                parent=road,
                model='cube',
                color=color.rgba32(255, 255, 255, 200),
                scale=(0.02, 1.01, 1),
                position=(-0.45, 0.01, 0),
                texture='white_cube'
            )
            Entity(
                parent=road,
                model='cube',
                color=color.rgba32(255, 255, 255, 200),
                scale=(0.02, 1.01, 1),
                position=(0.45, 0.01, 0),
                texture='white_cube'
            )
            for j in range(4):
                Entity(
                    parent=road,
                    model='cube',
                    color=color.yellow,
                    scale=(0.015, 1.01, 0.12),
                    position=(0, 0.01, (j/4) - 0.375),
                    texture='white_cube'
                )
            self.segments.append(seg)
    def update(self):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        for seg in self.segments:
            seg.z -= state.world_speed * time.dt
            if seg.z < camera.z - 80:
                seg.z += 60 * len(self.segments)
ground = Ground()
scenery_objects = []
class Cactus(Entity):
    def __init__(self, x, z):
        super().__init__(position=(x, 0, z))
        height = random.uniform(1.5, 3.5)
        Entity(
            parent=self,
            model='cube',
            scale=(0.4, height, 0.4),
            color=color.rgb32(60, 140, 60),
            y=height/2
        )
        Entity(
            parent=self,
            model='sphere',
            scale=0.5,
            color=color.rgb32(70, 150, 70),
            y=height
        )
        if random.random() > 0.3:
            arm_height = random.uniform(0.8, height * 0.6)
            arm_side = random.choice([-1, 1])
            Entity(
                parent=self,
                model='cube',
                scale=(0.8, 0.3, 0.3),
                color=color.rgb32(55, 135, 55),
                position=(arm_side * 0.5, arm_height, 0)
            )
            Entity(
                parent=self,
                model='cube',
                scale=(0.3, 1, 0.3),
                color=color.rgb32(55, 135, 55),
                position=(arm_side * 0.9, arm_height + 0.5, 0)
            )
        if random.random() > 0.5:
            arm_height = random.uniform(0.5, height * 0.5)
            arm_side = random.choice([-1, 1])
            Entity(
                parent=self,
                model='cube',
                scale=(0.6, 0.25, 0.25),
                color=color.rgb32(50, 130, 50),
                position=(arm_side * 0.4, arm_height, 0)
            )
            Entity(
                parent=self,
                model='cube',
                scale=(0.25, 0.7, 0.25),
                color=color.rgb32(50, 130, 50),
                position=(arm_side * 0.7, arm_height + 0.35, 0)
            )
class Rock(Entity):
    def __init__(self, x, z, size='medium'):
        super().__init__(position=(x, 0, z))
        sizes = {
            'small': (0.5, 1.5),
            'medium': (1.5, 3),
            'large': (3, 5)
        }
        min_s, max_s = sizes.get(size, sizes['medium'])
        base_scale = random.uniform(min_s, max_s)
        Entity(
            parent=self,
            model='sphere',
            scale=(
                base_scale * random.uniform(0.8, 1.2),
                base_scale * random.uniform(0.5, 0.8),
                base_scale * random.uniform(0.8, 1.2)
            ),
            color=color.rgb32(
                random.randint(100, 130),
                random.randint(90, 110),
                random.randint(80, 100)
            ),
            y=base_scale * 0.3,
            rotation_y=random.uniform(0, 360)
        )
        if random.random() > 0.5:
            offset_scale = base_scale * 0.6
            Entity(
                parent=self,
                model='sphere',
                scale=(
                    offset_scale * random.uniform(0.7, 1.0),
                    offset_scale * random.uniform(0.5, 0.7),
                    offset_scale * random.uniform(0.7, 1.0)
                ),
                color=color.rgb32(
                    random.randint(90, 120),
                    random.randint(80, 100),
                    random.randint(70, 90)
                ),
                position=(
                    random.uniform(-base_scale*0.4, base_scale*0.4),
                    offset_scale * 0.2,
                    random.uniform(-base_scale*0.4, base_scale*0.4)
                )
            )
class DesertTree(Entity):
    def __init__(self, x, z):
        super().__init__(position=(x, 0, z))
        trunk_height = random.uniform(2, 4)
        Entity(
            parent=self,
            model='cube',
            scale=(0.4, trunk_height, 0.4),
            color=color.rgb32(101, 67, 33),
            y=trunk_height/2
        )
        for i in range(random.randint(2, 4)):
            Entity(
                parent=self,
                model='sphere',
                scale=random.uniform(1, 2),
                color=color.rgb32(
                    random.randint(60, 90),
                    random.randint(100, 140),
                    random.randint(50, 70)
                ),
                position=(
                    random.uniform(-1, 1),
                    trunk_height + random.uniform(-0.5, 1),
                    random.uniform(-1, 1)
                )
            )
class Mountain(Entity):
    def __init__(self, x, z, size='medium'):
        super().__init__(position=(x, 0, z))
        sizes = {
            'small': (15, 25),
            'medium': (25, 45),
            'large': (45, 70)
        }
        min_h, max_h = sizes.get(size, sizes['medium'])
        height = random.uniform(min_h, max_h)
        width = height * random.uniform(0.8, 1.5)
        base_col = color.rgb32(
            random.randint(100, 140),
            random.randint(90, 120),
            random.randint(110, 150)
        )
        Entity(
            parent=self,
            model='cone',
            scale=(width, height, width * random.uniform(0.6, 1.0)),
            color=base_col,
            y=0
        )
        if height > 35:
            Entity(
                parent=self,
                model='cone',
                scale=(width * 0.3, height * 0.2, width * 0.3),
                color=color.rgb32(240, 245, 255),
                y=height * 0.75
            )
        if random.random() > 0.4:
            offset_x = random.uniform(-width*0.3, width*0.3)
            sec_height = height * random.uniform(0.5, 0.8)
            Entity(
                parent=self,
                model='cone',
                scale=(width * 0.6, sec_height, width * 0.5),
                color=color.rgb32(
                    max(0, int(base_col.r * 255) - 10),
                    max(0, int(base_col.g * 255) - 10),
                    int(base_col.b * 255)
                ),
                position=(offset_x, 0, width * 0.2)
            )
class Tumbleweed(Entity):
    def __init__(self, x, z):
        super().__init__(position=(x, 0.5, z))
        size = random.uniform(0.4, 0.8)
        self.ball = Entity(
            parent=self,
            model='sphere',
            scale=size,
            color=color.rgb32(160, 140, 100),
            y=size/2
        )
        for i in range(5):
            Entity(
                parent=self.ball,
                model='sphere',
                scale=0.3,
                color=color.rgb32(140, 120, 80),
                position=(
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3)
                )
            )
        self.roll_speed = random.uniform(2, 5)
        self.drift_speed = random.uniform(1, 3)
        self.drift_dir = random.choice([-1, 1])
    def update(self):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.ball.rotation_x += self.roll_speed * 50 * time.dt
        self.ball.rotation_z += self.roll_speed * 20 * time.dt
        self.x += self.drift_dir * self.drift_speed * time.dt
class Billboard(Entity):
    def __init__(self, x, z):
        super().__init__(position=(x, 0, z))
        for px in [-1.5, 1.5]:
            Entity(
                parent=self,
                model='cube',
                scale=(0.3, 6, 0.3),
                color=color.rgb32(80, 60, 40),
                position=(px, 3, 0)
            )
        Entity(
            parent=self,
            model='cube',
            scale=(5, 3, 0.2),
            color=color.rgb32(200, 180, 140),
            y=5
        )
        text_color = random.choice([color.red, color.blue, color.rgb32(0, 100, 0)])
        for i in range(random.randint(2, 4)):
            Entity(
                parent=self,
                model='cube',
                scale=(random.uniform(1.5, 3.5), 0.3, 0.25),
                color=text_color,
                position=(random.uniform(-1, 1), 4.5 + i * 0.5, 0.05)
            )
class Fence(Entity):
    def __init__(self, x, z, length=20):
        super().__init__(position=(x, 0, z))
        post_spacing = 4
        num_posts = int(length / post_spacing) + 1
        for i in range(num_posts):
            Entity(
                parent=self,
                model='cube',
                scale=(0.15, 1.2, 0.15),
                color=color.rgb32(90, 70, 50),
                position=(0, 0.6, i * post_spacing - length/2)
            )
        for rail_y in [0.4, 0.9]:
            Entity(
                parent=self,
                model='cube',
                scale=(0.1, 0.1, length),
                color=color.rgb32(100, 80, 60),
                y=rail_y
            )
class SceneryManager:
    def __init__(self):
        self.spawn_distance = 150
        self.despawn_distance = 80
        self.last_spawn_z = 0
        self.spawn_interval = 15
    def spawn_initial(self):
        for i in range(8):
            side = random.choice([-1, 1])
            x = side * random.uniform(80, 150)
            z = i * 80 + random.uniform(-20, 20)
            size = random.choice(['small', 'medium', 'large'])
            m = Mountain(x, z, size)
            scenery_objects.append(m)
        for z in range(0, 200, 20):
            self.spawn_scenery_at_z(z)
        self.last_spawn_z = 200
    def spawn_scenery_at_z(self, z):
        if random.random() > 0.3:
            x = random.uniform(-35, -15)
            self.spawn_random_object(x, z + random.uniform(-10, 10))
        if random.random() > 0.3:
            x = random.uniform(15, 35)
            self.spawn_random_object(x, z + random.uniform(-10, 10))
        if random.random() > 0.85:
            side = random.choice([-1, 1])
            f = Fence(side * 13, z, length=random.uniform(15, 30))
            scenery_objects.append(f)
        if random.random() > 0.95:
            x = random.uniform(-30, 30)
            t = Tumbleweed(x, z)
            scenery_objects.append(t)
    def spawn_random_object(self, x, z):
        choice = random.random()
        if choice < 0.35:
            obj = Cactus(x, z)
        elif choice < 0.55:
            obj = Rock(x, z, random.choice(['small', 'medium', 'large']))
        elif choice < 0.70:
            obj = DesertTree(x, z)
        elif choice < 0.80:
            obj = Billboard(x, z)
        else:
            obj = Entity(position=(x, 0, z))
            for i in range(random.randint(2, 4)):
                r = Rock(
                    random.uniform(-2, 2),
                    random.uniform(-2, 2),
                    'small'
                )
                r.parent = obj
            scenery_objects.append(obj)
            return
        scenery_objects.append(obj)
    def update(self):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        global scenery_objects
        while self.last_spawn_z < player.z + self.spawn_distance:
            self.spawn_scenery_at_z(self.last_spawn_z)
            self.last_spawn_z += self.spawn_interval
        for obj in scenery_objects[:]:
            try:
                if obj.z < player.z - self.despawn_distance:
                    scenery_objects.remove(obj)
                    destroy(obj)
            except:
                if obj in scenery_objects:
                    scenery_objects.remove(obj)
scenery_manager = SceneryManager()
collectibles = []
obstacles = []
def show_floating_text(text, position, text_color):
    try:
        t = Text(
            text=text,
            position=(0, 0.15),
            origin=(0, 0),
            scale=2.5,
            color=text_color
        )
        t.animate_position((0, 0.3), duration=0.8)
        t.animate_scale(0, duration=0.8)
        destroy(t, delay=0.8)
    except:
        pass
class Collectible(Entity):
    def __init__(self, x, z, y=2):
        super().__init__(position=(x, y, z))
        self.collected = False
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.base_y = y
    def update(self):
        if self.collected:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.y = self.base_y + math.sin(time.time() * 3 + self.bob_offset) * 0.3
        self.rotation_y += 150 * time.dt
        try:
            dist = distance_2d(self, player)
            y_diff = abs(self.y - player.y)
            if dist < 2 and y_diff < 2:
                self.on_collect()
                self.collected = True
                if self in collectibles:
                    collectibles.remove(self)
                destroy(self)
        except:
            pass
    def on_collect(self):
        pass
class Coin(Collectible):
    def __init__(self, x, z):
        super().__init__(x, z, y=2.5)
        self.visual = Entity(
            parent=self,
            model='sphere',
            color=color.yellow,
            scale=(0.6, 0.6, 0.2)
        )
        Entity(
            parent=self,
            model='sphere',
            color=color.white,
            scale=0.2,
            position=(0.2, 0.2, 0)
        )
    def on_collect(self):
        state.score += 50 * state.combo
        score_text.text = str(state.score)
        show_floating_text("+50", self.position, color.yellow)
class PowerUp(Collectible):
    def __init__(self, x, z, duration=5.0):
        super().__init__(x, z, y=3)
        self.duration = duration
        self.power_name = "POWER"
        self.power_color = color.white
    def on_collect(self):
        show_floating_text(self.power_name + "!", self.position, self.power_color)
        self.apply_effect()
    def apply_effect(self):
        pass
class ShieldPowerUp(PowerUp):
    def __init__(self, x, z):
        super().__init__(x, z, duration=15.0)
        self.power_name = "SHIELD"
        self.power_color = color.cyan
        Entity(
            parent=self,
            model='sphere',
            color=color.rgba32(0, 200, 255, 150),
            scale=1.0
        )
        Entity(
            parent=self,
            model='sphere',
            color=color.cyan,
            scale=0.5
        )
    def apply_effect(self):
        player.has_shield = True
        player.shield_visual.enabled = True
        def remove_shield():
            player.has_shield = False
            player.shield_visual.enabled = False
        invoke(remove_shield, delay=self.duration)
        msg_text.text = f"SHIELD ACTIVE!"
        msg_text.color = color.cyan
        invoke(lambda: setattr(msg_text, 'text', ''), delay=2)
class MagnetPowerUp(PowerUp):
    def __init__(self, x, z):
        super().__init__(x, z, duration=8.0)
        self.power_name = "MAGNET"
        self.power_color = color.red
        Entity(
            parent=self,
            model='cube',
            color=color.red,
            scale=(0.8, 0.3, 0.3)
        )
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(200, 200, 200),
            scale=(0.25, 0.5, 0.25),
            position=(-0.3, -0.3, 0)
        )
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(200, 200, 200),
            scale=(0.25, 0.5, 0.25),
            position=(0.3, -0.3, 0)
        )
    def apply_effect(self):
        player.has_magnet = True
        player.magnet_timer = self.duration
        msg_text.text = f"MAGNET ACTIVE!"
        msg_text.color = color.red
        invoke(lambda: setattr(msg_text, 'text', ''), delay=2)
class SlowMoPowerUp(PowerUp):
    def __init__(self, x, z):
        super().__init__(x, z, duration=4.0)
        self.power_name = "SLOW-MO"
        self.power_color = color.violet
        Entity(
            parent=self,
            model='sphere',
            color=color.violet,
            scale=(0.4, 0.7, 0.4)
        )
        Entity(
            parent=self,
            model='cone',
            color=color.rgb32(200, 150, 255),
            scale=(0.5, 0.4, 0.5),
            y=0.4,
            rotation_x=180
        )
        Entity(
            parent=self,
            model='cone',
            color=color.rgb32(200, 150, 255),
            scale=(0.5, 0.4, 0.5),
            y=-0.4
        )
    def apply_effect(self):
        player.slow_mo_active = True
        player.slow_mo_timer = self.duration
        application.time_scale = 0.4
        msg_text.text = "SLOW MOTION!"
        msg_text.color = color.violet
        invoke(lambda: setattr(msg_text, 'text', ''), delay=1)
class DoublePointsPowerUp(PowerUp):
    def __init__(self, x, z):
        super().__init__(x, z, duration=10.0)
        self.power_name = "2X POINTS"
        self.power_color = color.lime
        Entity(
            parent=self,
            model='cube',
            color=color.lime,
            scale=(0.8, 0.8, 0.3)
        )
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(0, 100, 0),
            scale=(0.3, 0.3, 0.35),
            position=(0, 0, 0)
        )
    def apply_effect(self):
        player.double_points = True
        player.double_points_timer = self.duration
        msg_text.text = "DOUBLE POINTS!"
        msg_text.color = color.lime
        invoke(lambda: setattr(msg_text, 'text', ''), delay=2)
class SuperJumpPowerUp(PowerUp):
    def __init__(self, x, z):
        super().__init__(x, z, duration=12.0)
        self.power_name = "SUPER JUMP"
        self.power_color = color.orange
        Entity(
            parent=self,
            model='cube',
            color=color.orange,
            scale=(0.5, 0.2, 0.5)
        )
        for i in range(3):
            Entity(
                parent=self,
                model='cube',
                color=color.rgb32(255, 200, 0),
                scale=(0.4, 0.15, 0.15),
                position=(0, 0.2 + i * 0.2, 0),
                rotation_z=30 if i % 2 == 0 else -30
            )
    def apply_effect(self):
        player.super_jump = True
        player.super_jump_timer = self.duration
        msg_text.text = "SUPER JUMP!"
        msg_text.color = color.orange
        invoke(lambda: setattr(msg_text, 'text', ''), delay=2)
class Obstacle(Entity):
    def __init__(self, x, z):
        super().__init__(position=(x, 0, z))
        self.destroyed = False
        self.damage_player = True
        self.damage_vehicles = True
    def update(self):
        if self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        try:
            if self.z < camera.z - 60:
                self.remove()
        except:
            pass
    def remove(self):
        if self.destroyed:
            return
        self.destroyed = True
        if self in obstacles:
            obstacles.remove(self)
        try:
            destroy(self)
        except:
            pass
class OilSlick(Obstacle):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.damage_player = False
        self.puddle = Entity(
            parent=self,
            model='quad',
            color=color.rgb32(20, 20, 30),
            scale=(4, 8),
            rotation_x=90,
            y=0.05
        )
        for i in range(3):
            Entity(
                parent=self.puddle,
                model='quad',
                color=color.rgb32(60, 60, 80),
                scale=(random.uniform(0.1, 0.2), random.uniform(0.1, 0.15)),
                position=(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), -0.01)
            )
        self.spin_cooldown = 0
    def update(self):
        super().update()
        if self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.spin_cooldown -= time.dt
        if player.current_vehicle and player.state == 'riding':
            v = player.current_vehicle
            dx = abs(v.x - self.x)
            dz = abs(v.z - self.z)
            if dx < 2.5 and dz < 4 and self.spin_cooldown <= 0:
                self.spin_cooldown = 1.0
                spin_dir = random.choice([-1, 1])
                v.x += spin_dir * random.uniform(3, 6)
                v.x = clamp(v.x, LEFT_BOUND, RIGHT_BOUND)
                cam_controller.shake(0.2, 0.5)
                msg_text.text = "OIL SLICK!"
                msg_text.color = color.rgb32(100, 100, 150)
                invoke(lambda: setattr(msg_text, 'text', ''), delay=1)
class Roadblock(Obstacle):
    def __init__(self, x, z):
        super().__init__(x, z)
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(255, 100, 0),
            scale=(6, 1.5, 0.5),
            y=0.75
        )
        for i in range(4):
            Entity(
                parent=self,
                model='cube',
                color=color.rgb32(40, 40, 40) if i % 2 == 0 else color.rgb32(255, 200, 0),
                scale=(1.4, 1.4, 0.55),
                position=(-4.5 + i * 3, 0.75, 0)
            )
        for px in [-2.5, 2.5]:
            Entity(
                parent=self,
                model='cube',
                color=color.rgb32(80, 80, 80),
                scale=(0.3, 1.5, 0.3),
                position=(px, 0.75, 0)
            )
    def update(self):
        super().update()
        if self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        if player.current_vehicle and player.state == 'riding':
            v = player.current_vehicle
            dx = abs(v.x - self.x)
            dz = abs(v.z - self.z)
            if dx < 4 and dz < 1.5:
                Explosion(self.position + Vec3(0, 1, 0), caused_by_player=True)
                if player.has_shield:
                    player.has_shield = False
                    player.shield_visual.enabled = False
                    msg_text.text = "SHIELD BROKEN!"
                    msg_text.color = color.cyan
                    invoke(lambda: setattr(msg_text, 'text', ''), delay=1.5)
                    cam_controller.shake(0.3, 0.8)
                    self.remove()
                else:
                    player.crash()
class Pothole(Obstacle):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.damage_player = False
        Entity(
            parent=self,
            model='quad',
            color=color.rgb32(30, 30, 30),
            scale=(2, 3),
            rotation_x=90,
            y=0.02
        )
        for i in range(4):
            Entity(
                parent=self,
                model='quad',
                color=color.rgb32(60, 60, 60),
                scale=(random.uniform(0.3, 0.6), random.uniform(0.2, 0.4)),
                rotation_x=90,
                y=0.03,
                position=(random.uniform(-1, 1), 0, random.uniform(-1.5, 1.5))
            )
        self.bump_cooldown = 0
    def update(self):
        super().update()
        if self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.bump_cooldown -= time.dt
        if player.current_vehicle and player.state == 'riding':
            v = player.current_vehicle
            dx = abs(v.x - self.x)
            dz = abs(v.z - self.z)
            if dx < 1.5 and dz < 2 and self.bump_cooldown <= 0:
                self.bump_cooldown = 0.5
                cam_controller.shake(0.15, 0.4)
class SpikeStrip(Obstacle):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.damage_player = False
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(50, 50, 50),
            scale=(5, 0.1, 1),
            y=0.05
        )
        for i in range(10):
            Entity(
                parent=self,
                model='cone',
                color=color.rgb32(180, 180, 180),
                scale=(0.15, 0.3, 0.15),
                position=(-2 + i * 0.45, 0.2, 0)
            )
        self.hit_vehicles = []
    def update(self):
        super().update()
        if self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        if player.current_vehicle and player.state == 'riding':
            v = player.current_vehicle
            if v in self.hit_vehicles:
                return
            dx = abs(v.x - self.x)
            dz = abs(v.z - self.z)
            if dx < 3 and dz < 1:
                self.hit_vehicles.append(v)
                v.base_speed = v.base_speed * 0.5
                cam_controller.shake(0.2, 0.4)
                msg_text.text = "TIRE POPPED!"
                msg_text.color = color.rgb32(150, 150, 150)
                invoke(lambda: setattr(msg_text, 'text', ''), delay=1)
class Ramp(Obstacle):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.damage_player = False
        self.damage_vehicles = False
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(255, 150, 0),
            scale=(4, 0.3, 5),
            rotation_x=-20,
            y=0.8,
            z=1
        )
        Entity(
            parent=self,
            model='cube',
            color=color.rgb32(100, 100, 100),
            scale=(4, 1.5, 0.5),
            y=0.75,
            z=3
        )
        Entity(
            parent=self,
            model='cube',
            color=color.yellow,
            scale=(0.5, 0.1, 2),
            rotation_x=-20,
            y=0.9,
            z=1
        )
        self.launch_cooldown = 0
    def update(self):
        super().update()
        if self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.launch_cooldown -= time.dt
        if player.current_vehicle and player.state == 'riding':
            v = player.current_vehicle
            dx = abs(v.x - self.x)
            dz = v.z - self.z
            if dx < 3 and -2 < dz < 6 and self.launch_cooldown <= 0:
                self.launch_cooldown = 1.0
                jump_speed = v.speed * 1.5
                player.last_vehicle = v
                v.is_ridden = False
                v.wild_timer = 0
                player.state = 'jumping'
                player.velocity = Vec3(0, 35, jump_speed)  
                player.current_vehicle = None
                player.space_pressed = False
                player.air_time = 0
                cam_controller.shake(0.4, 0.8)
                msg_text.text = "RAMP LAUNCH!"
                msg_text.color = color.orange
                invoke(lambda: setattr(msg_text, 'text', ''), delay=1)
class PowerUpIndicator(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.icons = {}
        self.y_start = 0.35
    def show_powerup(self, name, duration, icon_color):
        if name in self.icons:
            destroy(self.icons[name]['bg'])
            destroy(self.icons[name]['text'])
        y_pos = self.y_start - len(self.icons) * 0.06
        bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba32(0, 0, 0, 150),
            scale=(0.25, 0.05),
            position=(0.75, y_pos)
        )
        txt = Text(
            parent=self,
            text=f"{name}: {duration:.1f}s",
            position=(0.75, y_pos),
            origin=(0, 0),
            scale=1,
            color=icon_color
        )
        self.icons[name] = {'bg': bg, 'text': txt, 'timer': duration}
    def update(self):
        if current_menu_state != MenuState.PLAYING:
            return
        to_remove = []
        for name, data in self.icons.items():
            data['timer'] -= time.dt
            data['text'].text = f"{name}: {data['timer']:.1f}s"
            if data['timer'] <= 0:
                to_remove.append(name)
        for name in to_remove:
            destroy(self.icons[name]['bg'])
            destroy(self.icons[name]['text'])
            del self.icons[name]
        for i, (name, data) in enumerate(self.icons.items()):
            y_pos = self.y_start - i * 0.06
            data['bg'].y = y_pos
            data['text'].y = y_pos
powerup_indicator = PowerUpIndicator()
class CollectiblesManager:
    def __init__(self):
        self.last_spawn_z = 0
        self.spawn_interval = 30
        self.coin_spawn_interval = 15
        self.last_coin_z = 0
    def spawn_initial(self):
        for z in range(50, 200, 30):
            x = random.uniform(-8, 8)
            c = Coin(x, z)
            collectibles.append(c)
        self.last_spawn_z = 100
        self.last_coin_z = 200
    def update(self):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        global collectibles, obstacles
        while self.last_coin_z < player.z + 150:
            if random.random() > 0.4:
                x = random.uniform(-8, 8)
                c = Coin(x, self.last_coin_z)
                collectibles.append(c)
            if random.random() > 0.85:
                self.spawn_coin_trail(self.last_coin_z)
            self.last_coin_z += self.coin_spawn_interval
        while self.last_spawn_z < player.z + 120:
            self.spawn_random_item(self.last_spawn_z)
            self.last_spawn_z += self.spawn_interval
        collectibles = [c for c in collectibles if not c.collected]
        obstacles = [o for o in obstacles if not o.destroyed]
    def spawn_coin_trail(self, z):
        x = random.uniform(-6, 6)
        for i in range(5):
            c = Coin(x, z + i * 5)
            collectibles.append(c)
    def spawn_random_item(self, z):
        x = random.uniform(-8, 8)
        roll = random.random()
        if roll < 0.40:
            obstacle_type = random.choice([
                OilSlick,
                Roadblock,
                Pothole,
                SpikeStrip,
                Ramp
            ])
            if obstacle_type == Ramp and random.random() > 0.3:
                obstacle_type = random.choice([OilSlick, Pothole])
            if obstacle_type == Roadblock:
                x = random.uniform(-4, 4)
            o = obstacle_type(x, z)
            obstacles.append(o)
        elif roll < 0.65:
            powerup_type = random.choices(
                [ShieldPowerUp, MagnetPowerUp, SlowMoPowerUp, DoublePointsPowerUp, SuperJumpPowerUp],
                weights=[25, 20, 15, 25, 15]
            )[0]
            p = powerup_type(x, z)
            collectibles.append(p)
collectibles_manager = CollectiblesManager()
class CameraController:
    def __init__(self):
        self.shake_time = 0
        self.shake_intensity = 0
        self.base_offset = Vec3(0, 15, -20)
        self.target_pos = Vec3(0, 15, -20)
    def setup(self):
        camera.rotation_x = 35
        camera.fov = 70
        camera.position = self.base_offset
    def shake(self, duration=0.2, intensity=0.5):
        self.shake_time = duration
        self.shake_intensity = intensity
    def update(self, target):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.target_pos = Vec3(
            target.x * 0.5,
            self.base_offset.y,
            target.z + self.base_offset.z
        )
        camera.position = Vec3(
            lerp(camera.x, self.target_pos.x, time.dt * 5),
            lerp(camera.y, self.target_pos.y, time.dt * 5),
            lerp(camera.z, self.target_pos.z, time.dt * 8)
        )
        if self.shake_time > 0:
            self.shake_time -= time.dt
            camera.x += random.uniform(-self.shake_intensity, self.shake_intensity)
            camera.y += random.uniform(-self.shake_intensity, self.shake_intensity)
cam_controller = CameraController()
cam_controller.setup()
AmbientLight(color=color.rgb32(150, 150, 150))
scene.fog_color = SKY_COLOR
scene.fog_density = 0.01
class LassoCircle(Entity):
    def __init__(self):
        super().__init__(
            model='circle',
            color=color.rgba32(255, 255, 0, 80),
            scale=8,
            rotation_x=90,
            enabled=False,
            y=0.3
        )
        self.ring = Entity(
            parent=self,
            model='circle',
            color=color.yellow,
            scale=1.0
        )
        Entity(
            parent=self,
            model='circle',
            color=color.rgba32(255, 255, 0, 40),
            scale=0.85
        )
        self.radius = 8
        self.vehicle_in_range = None
    def update(self):
        if not self.enabled:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.rotation_z += 150 * time.dt
        pulse = 1 + math.sin(time.time() * 6) * 0.1
        self.scale = self.radius * pulse
        self.vehicle_in_range = None
        for v in vehicles:
            if v.destroyed or v.is_ridden:
                continue
            if v == player.last_vehicle:
                continue
            dx = v.x - self.x
            dz = v.z - self.z
            dist = math.sqrt(dx*dx + dz*dz)
            if dist < self.radius * 0.4:
                self.vehicle_in_range = v
                self.ring.color = color.lime
                break
        if not self.vehicle_in_range:
            self.ring.color = color.yellow
lasso_circle = LassoCircle()
class LassoRope(Entity):
    def __init__(self):
        super().__init__(enabled=False)
        self.rope_parts = []
        for i in range(15):
            part = Entity(
                parent=self,
                model='sphere',
                color=color.rgb32(139, 90, 43),
                scale=0.2
            )
            self.rope_parts.append(part)
    def show(self, start_pos, end_pos):
        self.enabled = True
        for i, part in enumerate(self.rope_parts):
            t = i / (len(self.rope_parts) - 1)
            arc = math.sin(t * math.pi) * 3
            part.world_position = Vec3(
                lerp(start_pos.x, end_pos.x, t),
                lerp(start_pos.y, end_pos.y, t) + arc,
                lerp(start_pos.z, end_pos.z, t)
            )
    def hide(self):
        self.enabled = False
lasso_rope = LassoRope()
class Explosion(Entity):
    def __init__(self, position, caused_by_player=False):
        super().__init__(position=position)
        try:
            dist_to_camera = abs(position.z - camera.z)
            dist_to_player = abs(position.z - player.z)
            is_visible = dist_to_camera < 60 and dist_to_player < 40
        except:
            is_visible = False
        if is_visible:
            self.main = Entity(
                parent=self,
                model='sphere',
                color=color.orange,
                scale=1,
                unlit=True
            )
            self.particles = []
            for i in range(8):
                p = Entity(
                    parent=self,
                    model='sphere',
                    color=random.choice([color.red, color.orange, color.yellow]),
                    scale=random.uniform(0.3, 0.8),
                    position=(
                        random.uniform(-1, 1),
                        random.uniform(0, 2),
                        random.uniform(-1, 1)
                    ),
                    unlit=True
                )
                self.particles.append(p)
            for i in range(5):
                Entity(
                    parent=self,
                    model='sphere',
                    color=color.rgb32(60, 60, 60),
                    scale=random.uniform(0.5, 1.2),
                    position=(
                        random.uniform(-0.5, 0.5),
                        random.uniform(1, 3),
                        random.uniform(-0.5, 0.5)
                    )
                )
            if caused_by_player or dist_to_player < 15:
                cam_controller.shake(0.3, 0.8)
        else:
            self.main = None
            self.particles = []
        self.lifetime = 0
        self.max_lifetime = 0.8
        self.is_visible = is_visible
    def update(self):
        if current_menu_state != MenuState.PLAYING:
            return
        try:
            self.lifetime += time.dt
            if self.is_visible and self.main:
                scale_factor = 1 + self.lifetime * 5
                self.main.scale = scale_factor
                fade = 1 - (self.lifetime / self.max_lifetime)
                fade = max(0, min(1, fade))
                self.main.color = color.rgba32(255, 150, 0, int(fade * 255))
                for p in self.particles:
                    p.y += 5 * time.dt
                    p.scale *= 0.95
            if self.lifetime >= self.max_lifetime:
                destroy(self)
        except:
            try:
                destroy(self)
            except:
                pass
vehicles = []
class Vehicle(Entity):
    def __init__(self, x, z, v_type='sedan'):
        super().__init__()
        self.config = VEHICLE_CONFIGS.get(v_type, VEHICLE_CONFIGS['sedan'])
        self.v_type = v_type
        self.position = Vec3(x, 0, z)
        model_loaded = False
        try:
            self.body = Entity(
                parent=self,
                model=self.config['model'],
                texture=COLORMAP_TEXTURE,
                scale=self.config['scale'],
                rotation_y=180,
                y=0.5
            )
            model_loaded = True
        except Exception as e:
            print(f"Could not load {self.config['model']}: {e}")
            self.body = Entity(
                parent=self,
                model='cube',
                scale=(2, 1, 4),
                color=self.config['col'],
                y=0.7
            )
        self.is_police = self.config.get('is_police', False)
        self.siren_lights = []
        self.siren_timer = 0
        if self.is_police:
            self.body.color = color.rgb32(30, 30, 120)
            light_bar = Entity(
                parent=self,
                model='cube',
                color=color.rgb32(40, 40, 40),
                scale=(1.2, 0.15, 0.4),
                y=1.4
            )
            self.red_light = Entity(
                parent=self,
                model='sphere',
                color=color.red,
                scale=0.2,
                position=(-0.4, 1.5, 0),
                unlit=True
            )
            self.siren_lights.append(self.red_light)
            self.blue_light = Entity(
                parent=self,
                model='sphere',
                color=color.blue,
                scale=0.2,
                position=(0.4, 1.5, 0),
                unlit=True
            )
            self.siren_lights.append(self.blue_light)
            Entity(
                parent=self,
                model='cube',
                color=color.white,
                scale=(0.05, 0.2, 1.5),
                position=(0.8, 0.7, 0)
            )
            Entity(
                parent=self,
                model='cube',
                color=color.white,
                scale=(0.05, 0.2, 1.5),
                position=(-0.8, 0.7, 0)
            )
        self.wheel_list = []
        wheel_positions = self.config.get('wheel_positions', [
            (-0.55, 0.2, 0.75), (0.55, 0.2, 0.75),
            (-0.55, 0.2, -0.65), (0.55, 0.2, -0.65)
        ])
        wheel_scale = self.config.get('wheel_scale', 0.4)
        for i, pos in enumerate(wheel_positions):
            try:
                wheel = Entity(
                    parent=self,
                    model=self.config['wheel'],
                    texture=COLORMAP_TEXTURE,
                    scale=wheel_scale,
                    position=pos,
                    rotation_y=0 if i % 2 == 0 else 180
                )
            except:
                wheel = Entity(
                    parent=self,
                    model='cube',
                    scale=(0.12, 0.35, 0.35),
                    color=color.rgb32(25, 25, 25),
                    position=pos
                )
            self.wheel_list.append(wheel)
        self.base_speed = self.config['speed']
        self.speed = self.base_speed
        self.is_ridden = False
        self.wild_timer = 0
        self.destroyed = False
        self.collider = 'box'
        self.lane_x = x
        self.body_base_y = 0.5
    def update(self):
        if state.game_over or self.destroyed:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        try:
            _ = self.z
        except:
            self.destroyed = True
            return
        wheel_spin = self.speed * 12 * time.dt
        for w in self.wheel_list:
            w.rotation_x += wheel_spin
        if self.is_police and not self.is_ridden:
            self.siren_timer += time.dt * 8
            if int(self.siren_timer) % 2 == 0:
                self.red_light.scale = 0.3
                self.blue_light.scale = 0.15
                self.red_light.color = color.rgb32(255, 50, 50)
                self.blue_light.color = color.rgb32(50, 50, 150)
            else:
                self.red_light.scale = 0.15
                self.blue_light.scale = 0.3
                self.red_light.color = color.rgb32(150, 50, 50)
                self.blue_light.color = color.rgb32(50, 50, 255)
        if self.is_ridden:
            anger_pct = min(self.wild_timer / self.config['wild_time'], 1.0)
            speed_mult = 1 + anger_pct
            self.speed = self.base_speed * speed_mult
            self.z += self.speed * time.dt
            self.wild_timer += time.dt
            intensity = anger_pct
            if self.is_police:
                intensity *= 1.5  
            self.body.rotation_z = math.sin(time.time() * 12) * intensity * 15
            self.body.rotation_x = math.sin(time.time() * 8) * intensity * 8
            self.body.y = self.body_base_y + abs(math.sin(time.time() * 10)) * intensity * 0.3
            if self.is_police:
                self.red_light.scale = 0.1
                self.blue_light.scale = 0.1
            if self.wild_timer >= self.config['wild_time']:
                player.buck_off()
        else:
            self.speed = self.base_speed
            self.z += self.speed * time.dt
            self.x = lerp(self.x, self.lane_x, time.dt)
            self.body.rotation = Vec3(0, 0, 0)
            self.body.y = self.body_base_y
            if self.is_police and player.current_vehicle:
                target_x = player.x
                self.lane_x = lerp(self.lane_x, target_x, time.dt * 0.5)
            for other in vehicles[:]:
                if other == self or other.destroyed or other.is_ridden:
                    continue
                if self.destroyed:
                    break
                try:
                    dx = abs(self.x - other.x)
                    dz = abs(self.z - other.z)
                except:
                    continue
                if dx < 2.5 and dz < 4:
                    other.explode()
                    self.explode()
                    return
        if self.z < camera.z - 50:
            self.remove()
    def remove(self):
        if self.destroyed:
            return
        self.destroyed = True
        if self in vehicles:
            vehicles.remove(self)
        try:
            destroy(self)
        except:
            pass
    def explode(self):
        if self.destroyed:
            return
        self.destroyed = True
        try:
            pos = Vec3(self.x, self.y, self.z)
        except:
            pos = Vec3(0, 0, 0)
        Explosion(pos + Vec3(0, 1, 0), caused_by_player=False)
        try:
            dist = distance_2d(self, player)
            if dist < 20:
                state.score += 25
                score_text.text = str(state.score)
        except:
            pass
        if self in vehicles:
            vehicles.remove(self)
        try:
            destroy(self)
        except:
            pass
class Player(Entity):
    def __init__(self):
        super().__init__(position=(0, 2, 0))
        self.visual = Entity(parent=self)
        self.body_part = Entity(
            parent=self.visual,
            model='cube',
            scale=(0.6, 0.8, 0.4),
            color=color.azure,
            y=0.4
        )
        Entity(
            parent=self.visual,
            model='sphere',
            scale=0.45,
            color=color.rgb32(255, 200, 160),
            y=1.0
        )
        Entity(
            parent=self.visual,
            model='cube',
            scale=(0.7, 0.08, 0.7),
            color=color.rgb32(101, 67, 33),
            y=1.25
        )
        Entity(
            parent=self.visual,
            model='cube',
            scale=(0.4, 0.35, 0.4),
            color=color.rgb32(101, 67, 33),
            y=1.4
        )
        self.left_arm = Entity(
            parent=self.visual,
            model='cube',
            scale=(0.2, 0.5, 0.2),
            color=color.azure,
            position=(-0.4, 0.5, 0),
            rotation_z=20
        )
        self.right_arm = Entity(
            parent=self.visual,
            model='cube',
            scale=(0.2, 0.5, 0.2),
            color=color.azure,
            position=(0.4, 0.5, 0),
            rotation_z=-20
        )
        self.has_shield = False
        self.has_magnet = False
        self.magnet_timer = 0
        self.slow_mo_active = False
        self.slow_mo_timer = 0
        self.double_points = False
        self.double_points_timer = 0
        self.super_jump = False
        self.super_jump_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.shield_visual = Entity(
            parent=self,
            model='sphere',
            color=color.rgba32(0, 200, 255, 80),
            scale=2.5,
            enabled=False
        )
        self.current_vehicle = None
        self.target_vehicle = None
        self.last_vehicle = None
        self.state = 'riding'
        self.velocity = Vec3(0, 0, 0)
        self.space_pressed = False
        self.air_time = 0
        self.max_air_time = 3.0
    def update_powerups(self):
        if self.has_magnet:
            self.magnet_timer -= time.dt
            powerup_indicator.show_powerup("MAGNET", self.magnet_timer, color.red)
            if self.magnet_timer <= 0:
                self.has_magnet = False
            elif self.state == 'jumping':
                nearest = None
                nearest_dist = 999
                for v in vehicles:
                    if v.destroyed or v.is_ridden or v == self.last_vehicle:
                        continue
                    dist = distance_2d(self, v)
                    if dist < nearest_dist and v.z > self.z:
                        nearest = v
                        nearest_dist = dist
                if nearest and nearest_dist < 15:
                    pull_strength = 8 * time.dt
                    self.x = lerp(self.x, nearest.x, pull_strength)
                    self.z = lerp(self.z, nearest.z - 2, pull_strength * 0.5)
        if self.slow_mo_active:
            self.slow_mo_timer -= time.dt / 0.4
            powerup_indicator.show_powerup("SLOW-MO", self.slow_mo_timer, color.violet)
            if self.slow_mo_timer <= 0:
                self.slow_mo_active = False
                application.time_scale = 1.0
        if self.double_points:
            self.double_points_timer -= time.dt
            powerup_indicator.show_powerup("2X POINTS", self.double_points_timer, color.lime)
            if self.double_points_timer <= 0:
                self.double_points = False
        if self.super_jump:
            self.super_jump_timer -= time.dt
            powerup_indicator.show_powerup("SUPER JUMP", self.super_jump_timer, color.orange)
            if self.super_jump_timer <= 0:
                self.super_jump = False
        if self.has_shield:
            self.shield_visual.scale = 2.5 + math.sin(time.time() * 5) * 0.2
    def update(self):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.update_powerups()
        move_input = 0
        # Keyboard input
        if held_keys['a'] or held_keys['left arrow']:
            move_input = -1
        elif held_keys['d'] or held_keys['right arrow']:
            move_input = 1
        else:
            # Head tilt control when no keyboard input
            head_tilt = head_tracker.get_tilt()
            if abs(head_tilt) > 0.01:
                move_input = head_tilt
        if self.state == 'riding':
            self.update_riding(move_input)
        elif self.state == 'jumping':
            self.update_jumping(move_input)
        elif self.state == 'lassoing':
            self.update_lassoing()
    def update_riding(self, move_input):
        if not self.current_vehicle or self.current_vehicle.destroyed:
            self.state = 'jumping'
            self.velocity = Vec3(0, 10, 5)
            return
        v = self.current_vehicle
        v.x += move_input * 20 * time.dt
        v.x = clamp(v.x, LEFT_BOUND, RIGHT_BOUND)
        self.x = v.x
        self.z = v.z
        self.y = v.y + 1.8 + v.body.y - v.body_base_y
        self.visual.rotation_z = v.body.rotation_z * 0.5
        self.visual.rotation_x = v.body.rotation_x * 0.3
        self.left_arm.rotation_z = 40
        self.right_arm.rotation_z = -40
        for other in vehicles:
            if other == v or other.destroyed:
                continue
            dx = abs(v.x - other.x)
            dz = v.z - other.z
            if dx < 2.5 and 0 < dz < 4:
                try:
                    pos = Vec3(other.x, other.y, other.z)
                    other.destroyed = True
                    if other in vehicles:
                        vehicles.remove(other)
                    destroy(other)
                    Explosion(pos + Vec3(0, 1, 0), caused_by_player=True)
                except:
                    pass
                self.crash()
                return
    def update_jumping(self, move_input):
        self.x += move_input * 15 * time.dt
        self.x = clamp(self.x, LEFT_BOUND, RIGHT_BOUND)
        self.velocity.y -= 40 * time.dt
        self.y += self.velocity.y * time.dt
        self.z += self.velocity.z * time.dt
        self.air_time += time.dt
        self.visual.rotation_x += 500 * time.dt
        self.left_arm.rotation_z = -60
        self.right_arm.rotation_z = 60
        if held_keys['space']:
            lasso_circle.enabled = True
            lasso_circle.position = Vec3(self.x, 0.3, self.z)
            self.space_pressed = True
        else:
            lasso_circle.enabled = False
        if self.space_pressed and not held_keys['space']:
            self.space_pressed = False
            if lasso_circle.vehicle_in_range and not lasso_circle.vehicle_in_range.destroyed:
                self.target_vehicle = lasso_circle.vehicle_in_range
                self.start_lasso()
        if self.y < 0.5:
            self.crash()
    def update_lassoing(self):
        if not self.target_vehicle or self.target_vehicle.destroyed:
            self.state = 'jumping'
            self.velocity = Vec3(0, 0, state.world_speed)
            lasso_rope.hide()
            lasso_circle.enabled = False
            return
        target_pos = self.target_vehicle.position + Vec3(0, 2.5, 0)
        zip_speed = 25 * time.dt
        self.x = lerp(self.x, target_pos.x, zip_speed)
        self.y = lerp(self.y, target_pos.y, zip_speed)
        self.z = lerp(self.z, target_pos.z, zip_speed)
        lasso_rope.show(self.position, self.target_vehicle.position)
        self.visual.rotation = Vec3(0, 0, 0)
        self.left_arm.rotation_z = -100
        self.right_arm.rotation_z = 100
        dist = distance_2d(self, self.target_vehicle)
        if dist < 2 and abs(self.y - (self.target_vehicle.y + 2)) < 1.5:
            self.land_on_vehicle(self.target_vehicle)
    def start_lasso(self):
        self.state = 'lassoing'
        lasso_circle.enabled = False
        cam_controller.shake(0.1, 0.3)
    def land_on_vehicle(self, vehicle):
        self.state = 'riding'
        self.current_vehicle = vehicle
        self.last_vehicle = None
        self.air_time = 0
        vehicle.is_ridden = True
        vehicle.wild_timer = 0
        lasso_rope.hide()
        lasso_circle.enabled = False
        self.visual.rotation = Vec3(0, 0, 0)
        state.combo += 1
        state.max_combo = max(state.max_combo, state.combo)
        points = vehicle.config['points'] * state.combo
        if self.double_points:
            points *= 2
        state.score += points
        update_score_ui(points)
        cam_controller.shake(0.2, 0.5)
        vehicle_text.text = vehicle.v_type.upper()
        vehicle_text.color = vehicle.config['col']
        invoke(lambda: setattr(vehicle_text, 'text', ''), delay=1.5)
    def jump(self):
        if self.state != 'riding':
            return
        jump_speed = state.world_speed
        jump_height = 18  
        if self.super_jump:
            jump_height = 30
        if self.current_vehicle:
            self.last_vehicle = self.current_vehicle
            jump_speed = self.current_vehicle.speed * 1.2
            self.current_vehicle.is_ridden = False
            self.current_vehicle.wild_timer = 0
        self.state = 'jumping'
        self.velocity = Vec3(0, jump_height, jump_speed)
        self.current_vehicle = None
        self.space_pressed = True
        self.air_time = 0
        cam_controller.shake(0.15, 0.3)
    def buck_off(self):
        buck_speed = state.world_speed
        if self.current_vehicle:
            buck_speed = self.current_vehicle.speed
            self.current_vehicle.is_ridden = False
        self.state = 'jumping'
        self.velocity = Vec3(
            random.uniform(-5, 5),
            25,
            buck_speed * 1.1
        )
        self.current_vehicle = None
        state.combo = 0
        msg_text.text = "BUCKED OFF!"
        msg_text.color = color.orange
        invoke(lambda: setattr(msg_text, 'text', ''), delay=1.5)
        cam_controller.shake(0.3, 1)
    def crash(self):
        if self.has_shield:
            self.has_shield = False
            self.shield_visual.enabled = False
            msg_text.text = "SHIELD SAVED YOU!"
            msg_text.color = color.cyan
            invoke(lambda: setattr(msg_text, 'text', ''), delay=1.5)
            self.state = 'jumping'
            self.velocity = Vec3(random.uniform(-3, 3), 15, state.world_speed)
            if self.current_vehicle:
                self.current_vehicle.is_ridden = False
            self.current_vehicle = None
            cam_controller.shake(0.3, 0.8)
            return
        global current_menu_state
        state.game_over = True
        current_menu_state = MenuState.GAME_OVER
        application.time_scale = 1.0
        final_score_text.text = f"SCORE: {state.score:,}"
        final_combo_text.text = f"Max Combo: x{state.max_combo}" if hasattr(state, 'max_combo') else ""
        if self.current_vehicle:
            try:
                Explosion(self.current_vehicle.position + Vec3(0, 1, 0), caused_by_player=True)
            except:
                pass
            self.current_vehicle.is_ridden = False
        cam_controller.shake(0.5, 1.5)
        if is_highscore(state.score):
            invoke(lambda: show_name_entry(state.score), delay=0.3)
        else:
            game_over_panel.enabled = True
player = Player()
class VehicleSpawner:
    def __init__(self):
        self.spawn_timer = 0
        self.min_spawn_delay = 0.4
        self.max_spawn_delay = 1.2
    def update(self):
        if state.game_over:
            return
        if current_menu_state != MenuState.PLAYING:
            return
        self.spawn_timer -= time.dt
        if self.spawn_timer <= 0:
            self.spawn_vehicle()
            self.spawn_timer = random.uniform(self.min_spawn_delay, self.max_spawn_delay)
    def spawn_vehicle(self):
        spawn_z = player.z + random.uniform(60, 100)
        lanes = [-8, -4, 0, 4, 8]
        spawn_x = random.choice(lanes)
        for v in vehicles:
            if abs(v.x - spawn_x) < 3 and abs(v.z - spawn_z) < 8:
                spawn_x = random.choice(lanes)
                break
        police_chance = min(0.15, 0.02 + (state.score / 10000))
        if random.random() < police_chance:
            v_type = 'police'
        else:
            normal_types = [k for k in VEHICLE_CONFIGS.keys() if k != 'police']
            v_type = random.choice(normal_types)
        v = Vehicle(spawn_x, spawn_z, v_type)
        vehicles.append(v)
    def spawn_initial_vehicles(self):
        positions = [(0, 40), (-5, 55), (5, 70), (0, 90), (-6, 110), (6, 130)]
        for x, z in positions:
            v_type = random.choice(list(VEHICLE_CONFIGS.keys()))
            v = Vehicle(x, z, v_type)
            vehicles.append(v)
spawner = VehicleSpawner()
def start_game():
    global vehicles, scenery_objects, collectibles, obstacles
    player.enabled = True
    ground.enabled = True
    for v in vehicles:
        destroy(v)
    vehicles.clear()
    for s in scenery_objects:
        destroy(s)
    scenery_objects.clear()
    for c in collectibles:
        destroy(c)
    collectibles.clear()
    for o in obstacles:
        destroy(o)
    obstacles.clear()
    application.time_scale = 1.0
    state.reset()
    score_text.text = '0'
    combo_text.text = ''
    msg_text.text = ''
    vehicle_text.text = ''
    game_over_panel.enabled = False
    for i, seg in enumerate(ground.segments):
        seg.z = i * 60 - 60
    start_vehicle = Vehicle(0, 10, 'sedan')
    start_vehicle.is_ridden = True
    vehicles.append(start_vehicle)
    player.current_vehicle = start_vehicle
    player.target_vehicle = None
    player.last_vehicle = None
    player.state = 'riding'
    player.position = Vec3(0, 3, 10)
    player.velocity = Vec3(0, 0, 0)
    player.visual.rotation = Vec3(0, 0, 0)
    player.space_pressed = False
    player.air_time = 0
    player.has_shield = False
    player.shield_visual.enabled = False
    player.has_magnet = False
    player.magnet_timer = 0
    player.slow_mo_active = False
    player.slow_mo_timer = 0
    player.double_points = False
    player.double_points_timer = 0
    player.super_jump = False
    player.super_jump_timer = 0
    camera.position = Vec3(0, 15, -10)
    cam_controller.target_pos = Vec3(0, 15, -10)
    spawner.spawn_initial_vehicles()
    scenery_manager.last_spawn_z = 0
    scenery_manager.spawn_initial()
    collectibles_manager.last_spawn_z = 50
    collectibles_manager.last_coin_z = 50
    collectibles_manager.spawn_initial()
score_text = Text(text='0', position=(-0.85, 0.45), scale=2.5, color=color.white)
combo_text = Text(text='', position=(0, 0.3), scale=2, origin=(0, 0), color=color.lime)
msg_text = Text(text='', position=(0, 0.1), scale=2.5, origin=(0, 0), color=color.red)
vehicle_text = Text(text='', position=(0, -0.05), scale=1.8, origin=(0, 0), color=color.white)
wild_bar = HealthBar(bar_color=color.green, position=(-0.35, 0.42), scale=(0.7, 0.025), roundness=0.5)
wild_bar.background_color = color.dark_gray
wild_label = Text(text='CALM', position=(0, 0.46), scale=1.3, origin=(0, 0), color=color.green)
tutorial = Text(
    text='[A/D] Steer | HOLD [SPACE] to Jump | RELEASE [SPACE] to Lasso!',
    position=(0, -0.42), origin=(0, 0), scale=1.2, color=color.white, background=True
)
invoke(lambda: setattr(tutorial, 'enabled', False), delay=8)
game_over_panel = Entity(parent=camera.ui, enabled=False)
Entity(parent=game_over_panel, model='quad', scale=(1.5, 1), color=color.rgba32(0, 0, 0, 220))
Text(parent=game_over_panel, text='GAME OVER', scale=4, origin=(0, 0), y=0.25, color=color.red)
final_score_text = Text(parent=game_over_panel, text='SCORE: 0', scale=2.5, origin=(0, 0), y=0.1, color=color.yellow)
final_combo_text = Text(parent=game_over_panel, text='', scale=1.5, origin=(0, 0), y=0.02, color=color.lime)
restart_button = Button(
    parent=game_over_panel,
    text='PLAY AGAIN',
    color=color.green,
    highlight_color=color.lime,
    scale=(0.25, 0.06),
    position=(0, -0.12),
    text_color=color.white
)
menu_button = Button(
    parent=game_over_panel,
    text='MAIN MENU',
    color=color.azure,
    highlight_color=color.cyan,
    scale=(0.25, 0.06),
    position=(0, -0.22),
    text_color=color.white
)
def on_restart_click():
    start_game_from_menu()
def on_menu_click():
    show_main_menu()
restart_button.on_click = on_restart_click
menu_button.on_click = on_menu_click
def show_main_menu():
    global current_menu_state
    current_menu_state = MenuState.MAIN_MENU
    main_menu.enabled = True
    highscore_panel.enabled = False
    name_entry_panel.enabled = False
    head_tracker.stop()  # <-- ADD THIS LINE
    try:
        game_over_panel.enabled = False
    except:
        pass
    hide_game_ui()
def show_highscores():
    global current_menu_state
    current_menu_state = MenuState.HIGH_SCORES
    main_menu.enabled = False
    highscore_panel.enabled = True
    scores = load_highscores()
    for i, t in enumerate(highscore_texts):
        if i < len(scores):
            rank = i + 1
            name = scores[i]['name']
            score = scores[i]['score']
            if rank == 1:
                t.color = color.yellow
            elif rank == 2:
                t.color = color.rgb32(200, 200, 200)
            elif rank == 3:
                t.color = color.rgb32(205, 127, 50)
            else:
                t.color = color.white
            t.text = f'{rank}. {name[:10]} - {score:,}'
        else:
            t.text = f'{i+1}. ---'
            t.color = color.gray
def show_name_entry(score):
    global current_menu_state, player_name_input
    current_menu_state = MenuState.ENTER_NAME
    player_name_input = ""
    player_name_text.text = "_"
    name_entry_score_text.text = f'Score: {score:,}'
    name_entry_panel.enabled = True
    game_over_panel.enabled = False
def submit_name():
    global current_menu_state, player_name_input
    if len(player_name_input) >= 1:
        name = player_name_input.upper()[:10]
        save_highscore(name, state.score)
        name_entry_panel.enabled = False
        show_highscores()
def hide_game_ui():
    try:
        score_text.enabled = False
        combo_text.enabled = False
        msg_text.enabled = False
        vehicle_text.enabled = False
        wild_bar.enabled = False
        wild_label.enabled = False
        powerup_indicator.enabled = False
    except:
        pass
def show_game_ui():
    try:
        score_text.enabled = True
        combo_text.enabled = True
        msg_text.enabled = True
        vehicle_text.enabled = True
        powerup_indicator.enabled = True
        wild_bar.enabled = True      
        wild_label.enabled = True    
        camera_status_text.enabled = True
        camera_status_text.text = "Detecting Face..."
    except:
        pass
def start_game_from_menu():
    global current_menu_state
    current_menu_state = MenuState.PLAYING
    main_menu.enabled = False
    highscore_panel.enabled = False
    name_entry_panel.enabled = False
    show_game_ui()
    head_tracker.start()  # <-- ADD THIS LINE
    start_game()
def on_play_click():
    start_game_from_menu()
def on_highscore_click():
    show_highscores()
def on_quit_click():
    application.quit()
def on_back_click():
    show_main_menu()
play_button.on_click = on_play_click
highscore_button.on_click = on_highscore_click
quit_button.on_click = on_quit_click
back_button.on_click = on_back_click
def update_score_ui(points):
    score_text.text = str(state.score)
    combo_text.text = f'+{points}'
    if state.combo > 1:
        combo_text.text += f' (x{state.combo})'
    combo_text.scale = 2.5
    combo_text.animate_scale(0, duration=1.2, delay=0.3)
def update_wild_meter():
    if player.state in ('jumping', 'lassoing'):
        wild_bar.enabled = True
        wild_label.enabled = True
        pct = max(0, min(1, 1 - (player.air_time / player.max_air_time)))
        wild_bar.value = int(pct * 100)
        if pct > 0.6:
            wild_bar.bar_color = color.cyan
            wild_label.text = 'AIR TIME'
            wild_label.color = color.cyan
        elif pct > 0.3:
            wild_bar.bar_color = color.yellow
            wild_label.text = 'FALLING!'
            wild_label.color = color.yellow
        else:
            wild_bar.bar_color = color.red
            wild_label.text = 'LAND NOW!'
            wild_label.color = color.red
    elif player.current_vehicle and player.state == 'riding':
        wild_bar.enabled = True
        wild_label.enabled = True
        v = player.current_vehicle
        pct = max(0, min(1, 1 - (v.wild_timer / v.config['wild_time'])))
        wild_bar.value = int(pct * 100)
        if pct > 0.6:
            wild_bar.bar_color = color.green
            wild_label.text = 'CALM'
            wild_label.color = color.green
        elif pct > 0.3:
            wild_bar.bar_color = color.orange
            wild_label.text = 'ANGRY!'
            wild_label.color = color.orange
        else:
            wild_bar.bar_color = color.red
            wild_label.text = 'FURIOUS!!'
            wild_label.color = color.red
    else:
        wild_bar.enabled = False
        wild_label.enabled = False
def update():
    if current_menu_state != MenuState.PLAYING:
        return
    if state.game_over:
        return
    cam_controller.update(player)
    spawner.update()
    scenery_manager.update()
    collectibles_manager.update()
    update_wild_meter()
    state.world_speed = min(50, 25 + (state.score / 200))
    global vehicles
    vehicles = [v for v in vehicles if not v.destroyed]
def input(key):
    global player_name_input
    if current_menu_state == MenuState.ENTER_NAME:
        if key == 'enter' or key == 'return':
            submit_name()
        elif key == 'backspace' and len(player_name_input) > 0:
            player_name_input = player_name_input[:-1]
            if player_name_input:
                player_name_text.text = player_name_input + "_"
            else:
                player_name_text.text = "_"
        elif len(key) == 1 and key.isalpha() and len(player_name_input) < 10:
            player_name_input += key.upper()
            player_name_text.text = player_name_input + "_"
        elif len(key) == 1 and key.isdigit() and len(player_name_input) < 10:
            player_name_input += key
            player_name_text.text = player_name_input + "_"
        elif key == 'space' and len(player_name_input) < 10 and len(player_name_input) > 0:
            player_name_input += " "
            player_name_text.text = player_name_input + "_"
        return
    if current_menu_state == MenuState.MAIN_MENU:
        if key == 'escape':
            application.quit()
        return
    if current_menu_state == MenuState.HIGH_SCORES:
        if key == 'escape':
            show_main_menu()
        return
    if current_menu_state == MenuState.GAME_OVER:
        if key == 'r':
            start_game_from_menu()
        if key == 'escape':
            show_main_menu()
        return
    if current_menu_state == MenuState.PLAYING:
        if key == 'space' and player.state == 'riding':
            player.jump()
        if key == 'r' and state.game_over:
            start_game_from_menu()
        if key == 'escape':
            if state.game_over:
                show_main_menu()
            else:
                state.game_over = True
                application.time_scale = 1.0
                show_main_menu()
hide_game_ui()
game_over_panel.enabled = False
main_menu.enabled = True
current_menu_state = MenuState.MAIN_MENU
player.enabled = False
ground.enabled = False
for v in vehicles:
    v.enabled = False
app.run()