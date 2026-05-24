class Obstacle extends GameObject {
  constructor(x, y, type, roadSpeed) {
    const sizes = {
      car: { w: 38, h: 65 },
      truck: { w: 42, h: 90 },
      cone: { w: 20, h: 20 },
      barrel: { w: 24, h: 24 },
      oil: { w: 36, h: 18 },
      rock: { w: 30, h: 28 }
    };
    const s = sizes[type] || { w: 30, h: 30 };
    super(x, y, s.w, s.h);
    this.name = 'Obstacle';
    this.type = type;
    this.roadSpeed = roadSpeed;
    this.ownSpeed = 0;
    this.active = true;

    if (type === 'car') {
      this.ownSpeed = roadSpeed * 0.3;
      this.color = this.randomCarColor();
    } else if (type === 'truck') {
      this.ownSpeed = roadSpeed * 0.15;
      this.color = '#556677';
    }
  }

  randomCarColor() {
    const colors = ['#3498db', '#2ecc71', '#f1c40f', '#9b59b6', '#1abc9c', '#e67e22', '#ffffff'];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  update(dt) {
    this.y += (this.roadSpeed - this.ownSpeed) * dt;
  }

  draw(ctx) {
    ctx.save();
    switch (this.type) {
      case 'car':
        this.drawCar(ctx);
        break;
      case 'truck':
        this.drawTruck(ctx);
        break;
      case 'cone':
        this.drawCone(ctx);
        break;
      case 'barrel':
        this.drawBarrel(ctx);
        break;
      case 'oil':
        this.drawOil(ctx);
        break;
      case 'rock':
        this.drawRock(ctx);
        break;
    }
    ctx.restore();
  }

  drawCar(ctx) {
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(this.x + 3, this.y + 3, this.width, this.height);
    ctx.fillStyle = this.color;
    this.roundRect(ctx, this.x, this.y, this.width, this.height, 5);
    ctx.fill();
    ctx.fillStyle = '#88ccff';
    ctx.fillRect(this.x + 5, this.y + this.height - 22, this.width - 10, 14);
    ctx.fillStyle = '#ff3333';
    ctx.fillRect(this.x + 3, this.y, 7, 4);
    ctx.fillRect(this.x + this.width - 10, this.y, 7, 4);
  }

  drawTruck(ctx) {
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(this.x + 3, this.y + 3, this.width, this.height);
    ctx.fillStyle = this.color;
    this.roundRect(ctx, this.x, this.y, this.width, this.height, 4);
    ctx.fill();
    ctx.fillStyle = '#445566';
    ctx.fillRect(this.x + 2, this.y + this.height - 28, this.width - 4, 26);
    ctx.fillStyle = '#88ccff';
    ctx.fillRect(this.x + 5, this.y + this.height - 24, this.width - 10, 10);
  }

  drawCone(ctx) {
    ctx.fillStyle = '#ff6600';
    ctx.beginPath();
    ctx.moveTo(this.x + this.width / 2, this.y);
    ctx.lineTo(this.x + this.width, this.y + this.height);
    ctx.lineTo(this.x, this.y + this.height);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.fillRect(this.x + 5, this.y + 8, this.width - 10, 4);
  }

  drawBarrel(ctx) {
    ctx.fillStyle = '#cc4400';
    ctx.beginPath();
    ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.width / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ffaa00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.width / 3, 0, Math.PI * 2);
    ctx.stroke();
  }

  drawOil(ctx) {
    ctx.fillStyle = 'rgba(30, 30, 30, 0.7)';
    ctx.beginPath();
    ctx.ellipse(this.x + this.width / 2, this.y + this.height / 2, this.width / 2, this.height / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'rgba(60, 60, 80, 0.5)';
    ctx.beginPath();
    ctx.ellipse(this.x + this.width / 2 - 4, this.y + this.height / 2 - 2, 8, 4, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  drawRock(ctx) {
    ctx.fillStyle = '#666';
    ctx.beginPath();
    ctx.moveTo(this.x + 5, this.y + this.height);
    ctx.lineTo(this.x, this.y + this.height * 0.6);
    ctx.lineTo(this.x + 8, this.y);
    ctx.lineTo(this.x + this.width - 5, this.y + 2);
    ctx.lineTo(this.x + this.width, this.y + this.height * 0.5);
    ctx.lineTo(this.x + this.width - 3, this.y + this.height);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#888';
    ctx.beginPath();
    ctx.moveTo(this.x + 8, this.y);
    ctx.lineTo(this.x + this.width - 5, this.y + 2);
    ctx.lineTo(this.x + this.width * 0.6, this.y + this.height * 0.4);
    ctx.closePath();
    ctx.fill();
  }

  roundRect(ctx, x, y, w, h, r) {
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