function LevelConfig_getLevel(levelNum) {
  const levels = [
    {
      name: 'Highway Start',
      roadSpeed: 200,
      distance: 3000,
      obstacleTypes: ['car', 'cone'],
      spawnRate: 1.2,
      powerUpRate: 4,
      bgColor1: '#2d5a27',
      bgColor2: '#1a3a15',
      roadColor: '#444',
      maxObstacles: 4
    },
    {
      name: 'City Streets',
      roadSpeed: 260,
      distance: 4000,
      obstacleTypes: ['car', 'truck', 'cone', 'barrel'],
      spawnRate: 0.9,
      powerUpRate: 5,
      bgColor1: '#3a3a4a',
      bgColor2: '#2a2a3a',
      roadColor: '#3a3a3a',
      maxObstacles: 6
    },
    {
      name: 'Mountain Pass',
      roadSpeed: 300,
      distance: 5000,
      obstacleTypes: ['car', 'rock', 'barrel', 'oil'],
      spawnRate: 0.75,
      powerUpRate: 5,
      bgColor1: '#4a3a2a',
      bgColor2: '#3a2a1a',
      roadColor: '#484440',
      maxObstacles: 7
    },
    {
      name: 'Desert Highway',
      roadSpeed: 360,
      distance: 6000,
      obstacleTypes: ['car', 'truck', 'rock', 'oil', 'barrel'],
      spawnRate: 0.6,
      powerUpRate: 6,
      bgColor1: '#c2a645',
      bgColor2: '#a08030',
      roadColor: '#555',
      maxObstacles: 8
    },
    {
      name: 'Night Race',
      roadSpeed: 420,
      distance: 7000,
      obstacleTypes: ['car', 'truck', 'cone', 'barrel', 'rock', 'oil'],
      spawnRate: 0.5,
      powerUpRate: 7,
      bgColor1: '#0a0a1a',
      bgColor2: '#050510',
      roadColor: '#222',
      maxObstacles: 10
    }
  ];
  return levels[Math.min(levelNum - 1, levels.length - 1)];
}

function LevelConfig_totalLevels() {
  return 5;
}