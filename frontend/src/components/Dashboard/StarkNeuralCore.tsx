import { useState, useEffect, useRef } from 'react';
import { Cpu, Activity, Zap, RefreshCw } from 'lucide-react';

interface Particle {
  x: number;
  y: number;
  z: number;
  base_x: number;
  base_y: number;
  base_z: number;
  radius: number;
  color: string;
  speed_x: number;
  speed_y: number;
  speed_z: number;
}

export function StarkNeuralCore() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [pulse, setPulse] = useState(false);
  const [activeModel, setActiveModel] = useState("LLaMA-3.1-8B");
  const [synapseCount, setSynapseCount] = useState(128);
  const [pulseIntensity, setPulseIntensity] = useState(1.0);
  const rotationRef = useRef({ x: 0.004, y: 0.006 });
  const mouseRef = useRef({ x: 0, y: 0, target_x: 0, target_y: 0 });

  // Polling de trazas para disparar pulsos neuronales reales ante peticiones
  useEffect(() => {
    let lastTraceId = '';
    const pollInterval = setInterval(async () => {
      try {
        const base = import.meta.env.VITE_API_URL || '';
        const res = await fetch(`${base}/v1/traces?limit=1`);
        if (res.ok) {
          const data = await res.json();
          const trace = data.traces?.[0];
          if (trace && trace.id !== lastTraceId) {
            lastTraceId = trace.id;
            // Disparar pulso neuronal visual en vivo
            setPulse(true);
            setPulseIntensity(2.5);
            if (trace.model) {
              setActiveModel(trace.model);
            }
            setTimeout(() => {
              setPulse(false);
              setPulseIntensity(1.0);
            }, 1000);
          }
        }
      } catch {
        // Silencioso
      }
    }, 1500);

    return () => clearInterval(pollInterval);
  }, []);

  // Simulación 3D y renderizado en Canvas HTML5 (Buttery-smooth 60 FPS en Apple Silicon M4)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 600);
    let height = (canvas.height = 420);

    const handleResize = () => {
      width = canvas.width = canvas.parentElement?.clientWidth || 600;
      height = canvas.height = 420;
    };
    window.addEventListener('resize', handleResize);

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current.target_x = (e.clientX - rect.left - width / 2) * 0.00005;
      mouseRef.current.target_y = (e.clientY - rect.top - height / 2) * 0.00005;
    };
    canvas.addEventListener('mousemove', handleMouseMove);

    // Inicializar 128 partículas en una distribución esférica holográfica de Fibonacci
    const count = 128;
    setSynapseCount(count);
    const particles: Particle[] = [];
    const sphereRadius = 130;

    for (let i = 0; i < count; i++) {
      const phi = Math.acos(-1 + (2 * i) / count);
      const theta = Math.sqrt(count * Math.PI) * phi;

      const x = sphereRadius * Math.sin(phi) * Math.cos(theta);
      const y = sphereRadius * Math.sin(phi) * Math.sin(theta);
      const z = sphereRadius * Math.cos(phi);

      particles.push({
        x, y, z,
        base_x: x,
        base_y: y,
        base_z: z,
        radius: Math.random() * 2 + 1,
        color: i % 3 === 0 ? 'cyan' : (i % 3 === 1 ? 'magenta' : 'royalblue'),
        speed_x: Math.random() * 0.02 - 0.01,
        speed_y: Math.random() * 0.02 - 0.01,
        speed_z: Math.random() * 0.02 - 0.01,
      });
    }

    // Parámetros de proyección 3D
    const fov = 350;
    const cameraDistance = 300;
    let angleX = 0;
    let angleY = 0;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Amortiguación del movimiento del ratón
      mouseRef.current.x += (mouseRef.current.target_x - mouseRef.current.x) * 0.1;
      mouseRef.current.y += (mouseRef.current.target_y - mouseRef.current.y) * 0.1;

      // Velocidad base de rotación + influencia del pulso e interactividad
      const speedMultiplier = pulseIntensity;
      angleY += (rotationRef.current.y + mouseRef.current.x) * speedMultiplier;
      angleX += (rotationRef.current.x + mouseRef.current.y) * speedMultiplier;

      // 1. Dibujar efectos HUD retro-futuristas de fondo (Tony Stark Style)
      ctx.save();
      ctx.translate(width / 2, height / 2);
      
      // Anillo concéntrico exterior giratorio
      ctx.strokeStyle = 'rgba(0, 255, 255, 0.15)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(0, 0, 180, 0, Math.PI * 2);
      ctx.stroke();

      // Anillo concéntrico punteado girando en dirección opuesta
      ctx.strokeStyle = 'rgba(255, 0, 255, 0.12)';
      ctx.setLineDash([6, 12]);
      ctx.beginPath();
      ctx.arc(0, 0, 150, -angleY * 0.3, Math.PI * 2 - angleY * 0.3);
      ctx.stroke();
      ctx.restore();

      // Matriz de proyección 3D para cada nodo
      const projected: { x: number; y: number; z: number; color: string; r: number }[] = [];

      particles.forEach((p) => {
        // Vibración sutil de las sinapsis (más activa si hay pulso)
        const jitter = (Math.random() - 0.5) * (pulse ? 4 : 0.8);
        let x = p.base_x + jitter;
        let y = p.base_y + jitter;
        let z = p.base_z + jitter;

        // Rotación alrededor del eje Y
        const cosY = Math.cos(angleY);
        const sinY = Math.sin(angleY);
        let x1 = x * cosY - z * sinY;
        let z1 = x * sinY + z * cosY;

        // Rotación alrededor del eje X
        const cosX = Math.cos(angleX);
        const sinX = Math.sin(angleX);
        let y2 = y * cosX - z1 * sinX;
        let z2 = y * sinX + z1 * cosX;

        // Proyección de perspectiva 3D a coordenadas 2D
        const scale = fov / (z2 + cameraDistance);
        const sx = width / 2 + x1 * scale;
        const sy = height / 2 + y2 * scale;

        projected.push({
          x: sx,
          y: sy,
          z: z2,
          color: p.color,
          r: p.radius * scale * 0.5,
        });
      });

      // 2. Dibujar líneas de conexión sinápticas (Axones) basadas en distancia 3D
      ctx.lineWidth = 0.5;
      for (let i = 0; i < projected.length; i++) {
        for (let j = i + 1; j < projected.length; j++) {
          const dx = projected[i].x - projected[j].x;
          const dy = projected[i].y - projected[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          // Si están cerca en la pantalla y en el espacio 3D, dibujamos un axón con opacidad
          if (dist < 70) {
            const opacity = (1 - dist / 70) * 0.22 * (pulse ? 2.2 : 1);
            ctx.strokeStyle = projected[i].color === 'cyan' 
              ? `rgba(0, 255, 255, ${opacity})` 
              : (projected[i].color === 'magenta' ? `rgba(255, 0, 255, ${opacity})` : `rgba(65, 105, 225, ${opacity})`);
            ctx.beginPath();
            ctx.moveTo(projected[i].x, projected[i].y);
            ctx.lineTo(projected[j].x, projected[j].y);
            ctx.stroke();
          }
        }
      }

      // 3. Dibujar las partículas del núcleo (Neuronas) con profundidad (Z-Sorting implícito para brillo)
      projected.forEach((node) => {
        // Brillo más intenso y color de acuerdo al eje Z (profundidad)
        const alpha = Math.max(0.15, (node.z + sphereRadius) / (sphereRadius * 2));
        
        ctx.fillStyle = node.color === 'cyan' 
          ? `rgba(0, 255, 255, ${alpha})` 
          : (node.color === 'magenta' ? `rgba(255, 0, 255, ${alpha})` : `rgba(65, 105, 225, ${alpha})`);

        if (pulse) {
          ctx.shadowBlur = 10;
          ctx.shadowColor = node.color === 'cyan' ? '#00ffff' : '#ff00ff';
        } else {
          ctx.shadowBlur = 0;
        }

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.shadowBlur = 0; // Restaurar sombra

      // 4. Dibujar destello del núcleo central (Core Radial Gradient)
      ctx.save();
      ctx.translate(width / 2, height / 2);
      const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, pulse ? 45 : 18);
      grad.addColorStop(0, pulse ? 'rgba(0, 255, 255, 0.8)' : 'rgba(255, 0, 255, 0.5)');
      grad.addColorStop(0.5, 'rgba(65, 105, 225, 0.2)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(0, 0, pulse ? 45 : 18, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
      canvas.removeEventListener('mousemove', handleMouseMove);
    };
  }, [pulse, pulseIntensity]);

  return (
    <div 
      className="rounded-xl p-4 overflow-hidden relative flex flex-col justify-between h-[420px]"
      style={{
        background: 'linear-gradient(135deg, var(--color-bg-secondary) 0%, rgba(10,15,30,0.85) 100%)',
        border: '1px solid var(--color-border)',
        boxShadow: pulse ? '0 0 20px rgba(0, 255, 255, 0.15)' : 'none',
        transition: 'box-shadow 0.5s ease-in-out'
      }}
    >
      {/* HUD Info Header */}
      <div className="flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <Cpu className={`w-4 h-4 ${pulse ? 'text-cyan-400 animate-pulse' : 'text-cyan-500'}`} style={{ color: 'var(--color-accent)' }} />
          <span className="text-xs font-semibold tracking-wider uppercase font-mono" style={{ color: 'var(--color-text)' }}>
            Jarvis Neural Core
          </span>
        </div>
        <div className="flex items-center gap-1.5 bg-black/40 px-2 py-0.5 rounded-full border border-white/5 font-mono text-[10px]" style={{ color: 'var(--color-text-secondary)' }}>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
          <span>Status: Optimal</span>
        </div>
      </div>

      {/* 3D Hologram Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full cursor-pointer" />

      {/* HUD Tech Metrics overlay (Tony Stark Tech overlay) */}
      <div className="grid grid-cols-2 gap-4 z-10 pointer-events-none">
        <div className="bg-black/35 backdrop-blur-md p-2.5 rounded-lg border border-white/5 font-mono">
          <div className="text-[10px] uppercase tracking-wide" style={{ color: 'var(--color-text-tertiary)' }}>
            Active Synapses
          </div>
          <div className="text-sm font-bold flex items-center gap-1.5 mt-0.5" style={{ color: 'var(--color-text)' }}>
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            {synapseCount} Nodes
          </div>
        </div>

        <div className="bg-black/35 backdrop-blur-md p-2.5 rounded-lg border border-white/5 font-mono">
          <div className="text-[10px] uppercase tracking-wide" style={{ color: 'var(--color-text-tertiary)' }}>
            Active Core Model
          </div>
          <div className="text-sm font-bold flex items-center gap-1.5 mt-0.5" style={{ color: 'var(--color-text)' }}>
            <Zap className={`w-3.5 h-3.5 ${pulse ? 'text-magenta-400 animate-bounce' : 'text-pink-500'}`} />
            {activeModel}
          </div>
        </div>
      </div>
    </div>
  );
}
