const PLAYER_DATA_DEFAULTS = {
  highScore: 0,
  bestLevel: 1,
  totalRaces: 0,
  leaderboard: [{ field: 'highScore', label: 'Highest Score' }]
};

class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.entities = [];
    this.scrollX = 0;
    this.scrollY = 0;
    this.lastTime = 0;
    this.keys = {};

    this.state = 'menu'; // menu, playing, levelComplete, gameOver, won
    this.score = 0;
    this.lives = 3;
    this.level = 1;
    this.distance = 0;
    this.levelConfig = null;
    this.obstacles = [];
    this.powerUps = [];
    this.particles = [];
    this.stripes = [];
    this.car = null;
    this.spawnTimer = 0;
    this.powerUpTimer = 0;
    this.boostTimer = 0;
    this.shakeTimer = 0;
    this.shakeIntensity = 0;

    this.roadWidth = 0;
    this.roadLeft = 0;
    this.roadRight = 0;

    this.playerData = null;

    this.setupInput();
    this.setupResize();
    this.setupUI();
    this.start();
  }

  async initSaveData() {
    try {
      if (window.SaveData && SaveData.isAvailable()) {
        this.playerData = await SaveData.getPlayerData(PLAYER_DATA_DEFAULTS);
      } else {
        this.playerData = Object.assign({}, PLAYER_DATA_DEFAULTS);
      }
    } catch (e) {
      this.playerData = Object.assign({}, PLAYER_DATA_DEFAULTS);
    }
    this.totalLevels = LevelConfig_totalLevels();
    this.updateMenuInfo();
  }

  updateMenuInfo() {
    const welcomeEl = document.getElementById('welcome-msg');
    if (welcomeEl && window.CurrentUser) {
      welcomeEl.textContent = 'Welcome, ' + CurrentUser.username + '!';
    }
    const savedEl = document.getElementById('savedProgress');
    if (savedEl && this.playerData) {
      if (this.playerData.highScore > 0) {
        savedEl.textContent = 'Best Score: ' + this.playerData.highScore + ' | Best Level: ' + this.playerData.bestLevel;
      }
    }
  }

  setupUI() {
    document.getElementById('btnStart').addEventListener('click', () => {
      this.startGame();
    });
    document.getElementById('btnNextLevel').addEventListener('click', () => {
      this.nextLevel();
    });
    document.getElementById('btnRestart').addEventListener('click', () => {
      this.restartGame();
    });
    document.getElementById('btnPlayAgain').addEventListener('click', () => {
      this.restartGame();
    });
  }

  setupInput() {
    window.addEventListener('keydown', (e) => {
      this.keys[e.code] = true;
      e.preventDefault();
    });
    window.addEventListener('keyup', (e) => {
      this.keys[e.code] = false;
    });
  }

  setupResize() {
    const fit = () => {
      const dpr = window.devicePixelRatio || 1;
      const r = this.canvas.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return;
      this.canvas.width = Math.floor(r.width * dpr);
      this.canvas.height = Math.floor(r.height * dpr);
      this.updateRoadDimensions();
    };
    window.addEventListener('resize', fit);
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(fit).observe(this.canvas);
    fit();
  }

  updateRoadDimensions() {
    this.roadWidth = Math.min(300, this.canvas.width * 0.45);
    this.roadLeft = (this.canvas.width - this.roadWidth) / 2;
    this.roadRight = this.roadLeft + this.roadWidth;
  }

  startGame() {
    this.score = 0;
    this.lives = 3;
    this.level = 1;
    this.loadLevel(1);
    this.showScreen('none');
    this.state = 'playing';
    if (this.playerData) {
      this.playerData.totalRaces++;
    }
  }

  loadLevel(num) {
    this.levelConfig = LevelConfig_getLevel(num);
    this.distance = 0;
    this.obstacles = [];
    this.powerUps = [];
    this.particles = [];
    this.spawnTimer = 0;
    this.powerUpTimer = 0;
    this.boostTimer = 0;
    this.entities = [];

    // Create car
    this.car = new Car(
      this.roadLeft + this.roadWidth / 2 - 20,
      this.canvas.height * 0.7
    );
    this.entities.push(this.car);

    // Create road stripes
    this.stripes = [];
    const centerX = this.canvas.width / 2;
    for (let y = -40; y < this.canvas.height + 40; y += 80) {
      const stripe = new RoadStripe(centerX - 2, y);
      this.stripes.push(stripe);
      this.entities.push(stripe);
    }

    this.updateHUD();
  }

  nextLevel() {
    this.level++;
    if (this.level > LevelConfig_totalLevels()) {
      this.winGame();
      return;
    }
    this.loadLevel(this.level);
    this.showScreen('none');
    this.state = 'playing';
  }

  restartGame() {
    this.startGame();
  }

  async winGame() {
    this.state = 'won';
    document.getElementById('wonScore').textContent = 'Final Score: ' + this.score;
    if (this.playerData) {
      document.getElementById('wonBest').textContent = 'Best Score: ' + this.playerData.highScore;
    }
    this.showScreen('gameWon');
    await this.saveProgress();
  }

  async gameOverHandler() {
    this.state = 'gameOver';
    document.getElementById('finalScore').textContent = 'Final Score: ' + this.score;
    if (this.playerData) {
      document.getElementById('bestScore').textContent = 'Best Score: ' + this.playerData.highScore;
    }
    this.showScreen('gameOver');
    await this.saveProgress();
  }

  async saveProgress() {
    if (this.playerData) {
      if (this.score > this.playerData.highScore) {
        this.playerData.highScore = this.score;
      }
      if (this.level > this.playerData.bestLevel) {
        this.playerData.bestLevel = this.level;
      }
      if (window.SaveData && SaveData.isAvailable()) {
        await SaveData.setPlayerData(this.playerData);
      }
    }
    if (window.Leaderboard && Leaderboard.isAvailable()) {
      await Leaderboard.finalize(this.score, { level: this.level });
    }
  }

  showScreen(screenId) {
    ['startScreen', 'levelComplete', 'gameOver', 'gameWon'].forEach(id => {
      document.getElementById(id).style.display = 'none';
    });
    if (screenId !== 'none') {
      document.getElementById(screenId).style.display = 'flex';
    }
  }

  updateHUD() {
    document.getElementById('hud-level').textContent = 'Level ' + this.level + ': ' + (this.levelConfig ? this.levelConfig.name : '');
    document.getElementById('hud-score').textContent = 'Score: ' + this.score;
    let hearts = '';
    for (let i = 0; i < this.lives; i++) hearts += '❤️';
    document.getElementById('hud-lives').textContent = hearts || '💀';
    const speed = this.car ? Math.floor(this.car.speed * 0.6) : 0;
    document.getElementById('hud-speed').textContent = speed + ' km/h';
  }

  spawnObstacle(dt) {
    if (!this.levelConfig) return;
    this.spawnTimer += dt;
    if (this.spawnTimer >= this.levelConfig.spawnRate && this.obstacles.length < this.levelConfig.maxObstacles) {
      this.spawnTimer = 0;
      const types = this.levelConfig.obstacleTypes;
      const type = types[Math.floor(Math.random() * types.length)];
      const x = this.roadLeft + 15 + Math.random() * (this.roadWidth - 60);
      const obs = new Obstacle(x, -100, type, this.levelConfig.roadSpeed);
      this.obstacles.push(obs);
      this.entities.push(obs);
    }
  }

  spawnPowerUp(dt) {
    if (!this.levelConfig) return;
    this.powerUpTimer += dt;
    if (this.powerUpTimer >= this.levelConfig.powerUpRate) {
      this.powerUpTimer = 0;
      const types = ['shield', 'boost', 'repair'];
      const type = types[Math.floor(Math.random() * types.length)];
      const x = this.roadLeft + 20 + Math.random() * (this.roadWidth - 60);
      const pu = new PowerUp(x, -50, type, this.levelConfig.roadSpeed);
      this.powerUps.push(pu);
      this.entities.push(pu);
    }
  }

  spawnParticles(x, y, color, count) {
    for (let i = 0; i < count; i++) {
      const p = new Particle(x, y, color);
      this.particles.push(p);
      this.entities.push(p);
    }
  }

  checkCollisions() {
    if (!this.car) return;
    const cb = this.car.getBounds();
    const carShrink = 5;
    const carBounds = {
      x: cb.x + carShrink,
      y: cb.y + carShrink,
      width: cb.width - carShrink * 2,
      height: cb.height - carShrink * 2
    };

    // Obstacle collisions
    for (let i = this.obstacles.length - 1; i >= 0; i--) {
      const obs = this.obstacles[i];
      if (!obs.active) continue;
      const ob = obs.getBounds();
      if (this.rectsOverlap(carBounds, ob)) {
        if (!this.car.invincible) {
          this.lives--;
          this.car.makeInvincible(2);
          this.shakeTimer = 0.3;
          this.shakeIntensity = 8;
          this.spawnParticles(this.car.x + this.car.width / 2, this.car.y, '#ff4444', 15);
          this.updateHUD();
          if (this.lives <= 0) {
            this.gameOverHandler();
            return;
          }
        }
        obs.active = false;
        this.removeEntity(obs);
        this.obstacles.splice(i, 1);
      }
    }

    // PowerUp collisions
    for (let i = this.powerUps.length - 1; i >= 0; i--) {
      const pu = this.powerUps[i];
      if (!pu.active) continue;
      const pb = pu.getBounds();
      if (this.rectsOverlap(carBounds, pb)) {
        pu.active = false;
        this.applyPowerUp(pu.type);
        this.spawnParticles(pu.x + pu.width / 2, pu.y + pu.height / 2, '#00ff88', 10);
        this.removeEntity(pu);
        this.powerUps.splice(i, 1);
      }
    }
  }

  applyPowerUp(type) {
    switch (type) {
      case 'shield':
        this.car.makeInvincible(4);
        break;
      case 'boost':
        this.boostTimer = 3;
        this.car.maxSpeed = 600;
        break;
      case 'repair':
        this.lives = Math.min(this.lives + 1, 5);
        this.updateHUD();
        break;
    }
    this.score += 50;
  }

  rectsOverlap(a, b) {
    return a.x < b.x + b.width && a.x + a.width > b.x &&
           a.y < b.y + b.height && a.y + a.height > b.y;
  }

  removeEntity(entity) {
    const idx = this.entities.indexOf(entity);
    if (idx !== -1) this.entities.splice(idx, 1);
  }

  cleanupOffscreen() {
    for (let i = this.obstacles.length - 1; i >= 0; i--) {
      if (this.obstacles[i].y > this.canvas.height + 50) {
        this.score += 10;
        this.removeEntity(this.obstacles[i]);
        this.obstacles.splice(i, 1);
      }
    }
    for (let i = this.powerUps.length - 1; i >= 0; i--) {
      if (this.powerUps[i].y > this.canvas.height + 50) {
        this.removeEntity(this.powerUps[i]);
        this.powerUps.splice(i, 1);
      }
    }
    for (let i = this.particles.length - 1; i >= 0; i--) {
      if (this.particles[i].life <= 0) {
        this.removeEntity(this.particles[i]);
        this.particles.splice(i, 1);
      }
    }
  }

  update(dt) {
    if (this.state !== 'playing') return;
    if (!this.levelConfig || !this.car) return;
    if (dt > 0.1) dt = 0.1; // cap dt

    const speed = this.levelConfig.roadSpeed;
    this.distance += speed * dt;

    // Update car
    this.car.update(dt, this.keys, this.roadLeft, this.roadRight);

    // Boost timer
    if (this.boostTimer > 0) {
      this.boostTimer -= dt;
      if (this.boostTimer <= 0) {
        this.car.maxSpeed = 400;
      }
    }

    // Shake
    if (this.shakeTimer > 0) {
      this.shakeTimer -= dt;
    }

    // Update stripes
    const centerX = this.canvas.width / 2;
    for (const stripe of this.stripes) {
      stripe.update(dt, speed);
      stripe.x = centerX - 2;
      if (stripe.y > this.canvas.height + 40) {
        stripe.y -= (this.stripes.length) * 80;
      }
    }

    // Spawn
    this.spawnObstacle(dt);
    this.spawnPowerUp(dt);

    // Update obstacles
    for (const obs of this.obstacles) obs.update(dt);
    for (const pu of this.powerUps) pu.update(dt);
    for (const p of this.particles) p.update(dt);

    // Collisions
    this.checkCollisions();
    this.cleanupOffscreen();

    // Score
    this.score += Math.floor(speed * dt * 0.1);
    this.updateHUD();

    // Leaderboard attest
    if (window.Leaderboard && Leaderboard.isAvailable()) {
      Leaderboard.attest(this.score, { level: this.level });
    }

    // Level complete
    if (this.distance >= this.levelConfig.distance) {
      this.completeLevelHandler();
    }
  }

  async completeLevelHandler() {
    this.state = 'levelComplete';
    const timeBonus = Math.floor(this.lives * 100 + this.car.speed * 0.5);
    this.score += timeBonus;
    document.getElementById('levelScore').textContent = 'Score: ' + this.score;
    document.getElementById('levelBonus').textContent = 'Completion Bonus: +' + timeBonus;
    this.showScreen('levelComplete');

    if (this.playerData) {
      if (this.score > this.playerData.highScore) {
        this.playerData.highScore = this.score;
      }
      if (this.level + 1 > this.playerData.bestLevel) {
        this.playerData.bestLevel = this.level + 1;
      }
      if (window.SaveData && SaveData.isAvailable()) {
        await SaveData.setPlayerData(this.playerData);
      }
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Camera shake
    if (this.shakeTimer > 0) {
      const sx = (Math.random() - 0.5) * this.shakeIntensity * 2;
      const sy = (Math.random() - 0.5) * this.shakeIntensity * 2;
      this.ctx.save();
      this.ctx.translate(sx, sy);
    }

    this.drawBackground();
    this.drawRoad();

    // Draw stripes
    for (const stripe of this.stripes) stripe.draw(this.ctx);

    // Draw powerups
    for (const pu of this.powerUps) pu.draw(this.ctx);

    // Draw obstacles
    for (const obs of this.obstacles) obs.draw(this.ctx);

    // Draw car
    if (this.car) this.car.draw(this.ctx);

    // Draw particles
    for (const p of this.particles) p.draw(this.ctx);

    // Boost effect
    if (this.boostTimer > 0 && this.car) {
      this.drawBoostEffect();
    }

    // Distance bar
    if (this.state === 'playing' && this.levelConfig) {
      this.drawProgressBar();
    }

    // Night level visibility effect
    if (this.level === 5 && this.state === 'playing') {
      this.drawNightEffect();
    }

    if (this.shakeTimer > 0) {
      this.ctx.restore();
    }
  }

  drawBackground() {
    const config = this.levelConfig || LevelConfig_getLevel(1);
    const grad = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
    grad.addColorStop(0, config.bgColor1);
    grad.addColorStop(1, config.bgColor2);
    this.ctx.fillStyle = grad;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Roadside details
    this.drawRoadsideDetails();
  }

  drawRoadsideDetails() {
    const config = this.levelConfig || LevelConfig_getLevel(1);
    // Trees/cacti/lamp posts based on level
    const offset = (this.distance * 0.5) % 200;
    this.ctx.fillStyle = config.bgColor1 === '#c2a645' ? '#886622' : '#1a4a14';

    for (let y = -offset; y < this.canvas.height + 100; y += 200) {
      // Left side
      if (this.level === 4) {
        // Cacti
        this.ctx.fillStyle = '#2d5a27';
        this.ctx.fillRect(this.roadLeft - 60, y, 8, 30);
        this.ctx.fillRect(this.roadLeft - 64, y + 8, 5, 15);
        this.ctx.fillRect(this.roadLeft - 48, y + 12, 5, 12);
      } else if (this.level === 5) {
        // Lamp posts
        this.ctx.fillStyle = '#555';
        this.ctx.fillRect(this.roadLeft - 30, y, 4, 60);
        this.ctx.fillStyle = '#ffff88';
        this.ctx.beginPath();
        this.ctx.arc(this.roadLeft - 28, y, 8, 0, Math.PI * 2);
        this.ctx.fill();
      } else {
        // Trees
        this.ctx.fillStyle = '#4a2a10';
        this.ctx.fillRect(this.roadLeft - 45, y + 15, 8, 25);
        this.ctx.fillStyle = '#1a6a14';
        this.ctx.beginPath();
        this.ctx.arc(this.roadLeft - 41, y + 10, 16, 0, Math.PI * 2);
        this.ctx.fill();
      }

      // Right side mirror
      if (this.level === 4) {
        this.ctx.fillStyle = '#2d5a27';
        this.ctx.fillRect(this.roadRight + 52, y + 40, 8, 30);
        this.ctx.fillRect(this.roadRight + 48, y + 48, 5, 15);
      } else if (this.level === 5) {
        this.ctx.fillStyle = '#555';
        this.ctx.fillRect(this.roadRight + 26, y + 40, 4, 60);
        this.ctx.fillStyle = '#ffff88';
        this.ctx.beginPath();
        this.ctx.arc(this.roadRight + 28, y + 40, 8, 0, Math.PI * 2);
        this.ctx.fill();
      } else {
        this.ctx.fillStyle = '#4a2a10';
        this.ctx.fillRect(this.roadRight + 37, y + 55, 8, 25);
        this.ctx.fillStyle = '#1a6a14';
        this.ctx.beginPath();
        this.ctx.arc(this.roadRight + 41, y + 50, 16, 0, Math.PI * 2);
        this.ctx.fill();
      }
    }
  }

  drawRoad() {
    const config = this.levelConfig || LevelConfig_getLevel(1);
    // Road surface
    this.ctx.fillStyle = config.roadColor;
    this.ctx.fillRect(this.roadLeft, 0, this.roadWidth, this.canvas.height);

    // Road edges
    this.ctx.fillStyle = '#fff';
    this.ctx.fillRect(this.roadLeft, 0, 3, this.canvas.height);
    this.ctx.fillRect(this.roadRight - 3, 0, 3, this.canvas.height);

    // Shoulder
    this.ctx.fillStyle = '#aa3333';
    this.ctx.fillRect(this.roadLeft - 8, 0, 8, this.canvas.height);
    this.ctx.fillRect(this.roadRight, 0, 8, this.canvas.height);
  }

  drawBoostEffect() {
    this.ctx.save();
    this.ctx.globalAlpha = 0.5;
    const cx = this.car.x + this.car.width / 2;
    const cy = this.car.y + this.car.height;
    const grad = this.ctx.createRadialGradient(cx, cy, 2, cx, cy + 30, 25);
    grad.addColorStop(0, '#ff8800');
    grad.addColorStop(0.5, '#ff4400');
    grad.addColorStop(1, 'transparent');
    this.ctx.fillStyle = grad;
    this.ctx.fillRect(cx - 25, cy, 50, 40);
    this.ctx.restore();
  }

  drawProgressBar() {
    const barWidth = 150;
    const barHeight = 12;
    const bx = this.canvas.width / 2 - barWidth / 2;
    const by = this.canvas.height - 30;
    const progress = Math.min(1, this.distance / this.levelConfig.distance);

    this.ctx.fillStyle = 'rgba(0,0,0,0.5)';
    this.ctx.fillRect(bx - 2, by - 2, barWidth + 4, barHeight + 4);
    this.ctx.fillStyle = '#333';
    this.ctx.fillRect(bx, by, barWidth, barHeight);
    const grad = this.ctx.createLinearGradient(bx, 0, bx + barWidth * progress, 0);
    grad.addColorStop(0, '#00ff88');
    grad.addColorStop(1, '#00cc66');
    this.ctx.fillStyle = grad;
    this.ctx.fillRect(bx, by, barWidth * progress, barHeight);

    this.ctx.fillStyle = '#fff';
    this.ctx.font = '10px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.fillText(Math.floor(progress * 100) + '%', bx + barWidth / 2, by + barHeight - 1);

    // Finish flag
    this.ctx.fillText('🏁', bx + barWidth + 15, by + barHeight);
  }

  drawNightEffect() {
    if (!this.car) return;
    const cx = this.car.x + this.car.width / 2;
    const cy = this.car.y;
    const grad = this.ctx.createRadialGradient(cx, cy - 40, 30, cx, cy - 40, 250);
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(0.7, 'rgba(0,0,10,0.5)');
    grad.addColorStop(1, 'rgba(0,0,10,0.85)');
    this.ctx.fillStyle = grad;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  screenToWorld(canvasX, canvasY) {
    return { x: canvasX + this.scrollX, y: canvasY + this.scrollY };
  }

  worldToScreen(worldX, worldY) {
    return { x: worldX - this.scrollX, y: worldY - this.scrollY };
  }

  getObjectAt(canvasX, canvasY) {
    const world = this.screenToWorld(canvasX, canvasY);
    for (const entity of this.entities) {
      const b = entity.getBounds();
      if (world.x >= b.x && world.x <= b.x + b.width &&
          world.y >= b.y && world.y <= b.y + b.height) {
        return entity;
      }
    }
    return null;
  }

  async start() {
    // Load saved data
    try {
      if (window.SaveData && SaveData.isAvailable()) {
        this.playerData = await SaveData.getPlayerData(PLAYER_DATA_DEFAULTS);
      } else {
        this.playerData = Object.assign({}, PLAYER_DATA_DEFAULTS);
      }
    } catch (e) {
      this.playerData = Object.assign({}, PLAYER_DATA_DEFAULTS);
    }
    // Wire in LevelConfig
    this.totalLevels = LevelConfig_totalLevels();
    this.defaultConfig = LevelConfig_getLevel(1);
    this.updateMenuInfo();

    const gameLoop = (timestamp) => {
      const dt = (timestamp - this.lastTime) / 1000;
      this.lastTime = timestamp;
      this.update(dt);
      this.draw();
      requestAnimationFrame(gameLoop);
    };
    requestAnimationFrame(gameLoop);
  }
}