class RoadStripe extends GameObject {
  constructor(x, y) {
    super(x, y, 4, 40);
    this.name = 'RoadStripe';
  }

  update(dt, speed) {
    this.y += speed * dt;
  }

  draw(ctx) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }
}