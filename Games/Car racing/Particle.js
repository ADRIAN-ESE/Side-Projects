class Particle extends GameObject {
  constructor(x, y, color) {
    super(x, y, 4, 4);
    this.name = 'Particle';
    this.color = color;
    this.vx = (Math.random() - 0.5) * 300;
    this.vy = (Math.random() - 0.5) * 300;
    this.life = 0.5 + Math.random() * 0.5;
    this.maxLife = this.life;
    this.size = 2 + Math.random() * 4;
  }

  update(dt) {
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.life -= dt;
    this.vx *= 0.97;
    this.vy *= 0.97;
  }

  draw(ctx) {
    const alpha = Math.max(0, this.life / this.maxLife);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    ctx.globalAlpha = 1;
  }
}