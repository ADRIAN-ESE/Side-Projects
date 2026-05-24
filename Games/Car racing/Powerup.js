class PowerUp extends GameObject {
  constructor(x, y, type, roadSpeed) {
    super(x, y, 28, 28);
    this.name = 'PowerUp';
    this.type = type; // 'shield', 'boost', 'repair'
    this.roadSpeed = roadSpeed;
    this.active = true;
    this.bobTimer = Math.random() * Math.PI * 2;
  }

  update(dt) {
    this.y += this.roadSpeed * dt;
    this.bobTimer += dt * 4;
  }

  draw(ctx) {
    const bobOffset = Math.sin(this.bobTimer) * 3;
    const cx = this.x + this.width / 2;
    const cy = this.y + this.height / 2 + bobOffset;
    const r = this.width / 2;

    // Glow
    ctx.save();
    ctx.shadowBlur = 15;

    switch (this.type) {
      case 'shield':
        ctx.shadowColor = '#00bfff';
        ctx.fillStyle = '#00bfff';
        ctx.beginPath();
        ctx.moveTo(cx, cy - r);
        ctx.lineTo(cx + r, cy - r * 0.3);
        ctx.lineTo(cx + r * 0.7, cy + r);
        ctx.lineTo(cx, cy + r * 0.6);
        ctx.lineTo(cx - r * 0.7, cy + r);
        ctx.lineTo(cx - r, cy - r * 0.3);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('S', cx, cy);
        break;
      case 'boost':
        ctx.shadowColor = '#ff8800';
        ctx.fillStyle = '#ff8800';
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('⚡', cx, cy);
        break;
      case 'repair':
        ctx.shadowColor = '#00ff88';
        ctx.fillStyle = '#00ff88';
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('+', cx, cy);
        break;
    }
    ctx.restore();
  }
}