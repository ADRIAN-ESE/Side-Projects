class Car extends GameObject {
  constructor(x, y) {
    super(x, y, 40, 70);
    this.name = 'Car';
    this.speed = 0;
    this.maxSpeed = 400;
    this.acceleration = 300;
    this.deceleration = 200;
    this.steerSpeed = 250;
    this.vx = 0;
    this.invincible = false;
    this.invincibleTimer = 0;
    this.blinkTimer = 0;
    this.visible = true;
    this.tilt = 0;
  }

  update(dt, keys, roadLeft, roadRight) {
    // Acceleration
    if (keys['ArrowUp'] || keys['KeyW']) {
      this.speed = Math.min(this.speed + this.acceleration * dt, this.maxSpeed);
    } else if (keys['ArrowDown'] || keys['KeyS']) {
      this.speed = Math.max(this.speed - this.deceleration * 2 * dt, 50);
    } else {
      this.speed = Math.max(this.speed - this.deceleration * 0.5 * dt, 50);
    }

    // Steering
    let steerInput = 0;
    if (keys['ArrowLeft'] || keys['KeyA']) steerInput = -1;
    if (keys['ArrowRight'] || keys['KeyD']) steerInput = 1;

    this.vx = steerInput * this.steerSpeed;
    this.tilt = steerInput * 0.15;
    this.x += this.vx * dt;

    // Clamp to road
    if (this.x < roadLeft + 5) this.x = roadLeft + 5;
    if (this.x + this.width > roadRight - 5) this.x = roadRight - 5 - this.width;

    // Invincibility
    if (this.invincible) {
      this.invincibleTimer -= dt;
      this.blinkTimer += dt;
      this.visible = Math.sin(this.blinkTimer * 20) > 0;
      if (this.invincibleTimer <= 0) {
        this.invincible = false;
        this.visible = true;
      }
    }
  }

  makeInvincible(duration) {
    this.invincible = true;
    this.invincibleTimer = duration;
    this.blinkTimer = 0;
  }

  draw(ctx) {
    if (!this.visible) return;
    ctx.save();
    ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
    ctx.rotate(this.tilt);

    // Shadow
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(-this.width / 2 + 3, -this.height / 2 + 3, this.width, this.height);

    // Car body
    const grad = ctx.createLinearGradient(-this.width / 2, 0, this.width / 2, 0);
    grad.addColorStop(0, '#e94560');
    grad.addColorStop(0.5, '#ff6b81');
    grad.addColorStop(1, '#e94560');
    ctx.fillStyle = grad;
    this.drawRoundRect(ctx, -this.width / 2, -this.height / 2, this.width, this.height, 6);
    ctx.fill();

    // Windshield
    ctx.fillStyle = '#88ccff';
    this.drawRoundRect(ctx, -this.width / 2 + 6, -this.height / 2 + 12, this.width - 12, 16, 3);
    ctx.fill();

    // Rear window
    ctx.fillStyle = '#6699cc';
    this.drawRoundRect(ctx, -this.width / 2 + 8, this.height / 2 - 22, this.width - 16, 12, 2);
    ctx.fill();

    // Headlights
    ctx.fillStyle = '#ffff88';
    ctx.fillRect(-this.width / 2 + 3, -this.height / 2, 8, 5);
    ctx.fillRect(this.width / 2 - 11, -this.height / 2, 8, 5);

    // Taillights
    ctx.fillStyle = '#ff3333';
    ctx.fillRect(-this.width / 2 + 3, this.height / 2 - 5, 8, 5);
    ctx.fillRect(this.width / 2 - 11, this.height / 2 - 5, 8, 5);

    ctx.restore();
  }

  drawRoundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }
}