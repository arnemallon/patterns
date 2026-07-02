<script>
  import { onMount } from 'svelte';
  import { Chart, LineController, LineElement, PointElement, LinearScale, Title, Tooltip, CategoryScale, Legend } from 'chart.js';

  Chart.register(LineController, LineElement, PointElement, LinearScale, Title, Tooltip, CategoryScale, Legend);

  export let data = {};
  let canvasEl;

  // Sort the "Mon YYYY" labels chronologically, since JSON object key order
  // is not guaranteed to be preserved by the server
  function sortedEntries(obj) {
    return Object.entries(obj).sort(
      ([a], [b]) => new Date(`1 ${a}`) - new Date(`1 ${b}`)
    );
  }

  onMount(() => {
    if (data && Object.keys(data).length > 0) {
      const entries = sortedEntries(data);
      new Chart(canvasEl, {
        type: 'line',
        data: {
          labels: entries.map(([label]) => label),
          datasets: [{
            label: 'Addresses Analyzed',
            data: entries.map(([, value]) => value),
            fill: false,
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            tension: 0.3,
            pointRadius: 0,
            pointHoverRadius: 8,
            pointHitRadius: 16,
            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointHoverBorderColor: '#fff',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(30, 41, 59, 0.95)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: 'rgba(255,255,255,0.2)',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: false
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#b0b8c1', font: { size: 11, weight: 'bold' }, maxTicksLimit: 12 }
            },
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(255,255,255,0.08)', drawBorder: false },
              ticks: { color: '#b0b8c1', font: { size: 11, weight: 'bold' } }
            }
          }
        }
      });
    }
  });
</script>

<div class="line-chart-container">
  <canvas bind:this={canvasEl}></canvas>
</div>

<style>
  .line-chart-container {
    height: 180px;
    width: 100%;
  }
</style> 