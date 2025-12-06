<script>
	import { onMount } from 'svelte';

	let video;
	let canvas;
	let stream;
	let capturedImage = null;
	let prediction = null;
	let loading = false;
	let error = null;

	// Configuration
	const API_URL = 'https://harshitraj97-banana-api.hf.space/predict';
	const MODEL_INPUT_SIZE = 224;

	onMount(async () => {
		return () => {
			if (stream) stream.getTracks().forEach((track) => track.stop());
		};
	});

	async function startCamera() {
		try {
			error = null;
			stream = await navigator.mediaDevices.getUserMedia({
				video: { facingMode: 'environment' }
			});
			video.srcObject = stream;
			video.play();
		} catch (err) {
			console.error("Camera error:", err);
			error = "Could not access camera. Please allow permissions.";
		}
	}

	function captureImage() {
		if (!video) return;
		const context = canvas.getContext('2d');
		const size = Math.min(video.videoWidth, video.videoHeight);
		const startX = (video.videoWidth - size) / 2;
		const startY = (video.videoHeight - size) / 2;

		canvas.width = MODEL_INPUT_SIZE;
		canvas.height = MODEL_INPUT_SIZE;

		context.drawImage(
			video,
			startX, startY, size, size,
			0, 0, MODEL_INPUT_SIZE, MODEL_INPUT_SIZE
		);

		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}
		capturedImage = canvas.toDataURL('image/jpeg');
	}

	async function getPrediction() {
		if (!capturedImage) return;
		loading = true;
		error = null;

		canvas.toBlob(async (blob) => {
			const formData = new FormData();
			formData.append('file', blob, 'banana.jpg');

			try {
				const response = await fetch(API_URL, {
					method: 'POST',
					body: formData
				});
				if (!response.ok) throw new Error('API request failed');
				prediction = await response.json();
			} catch (err) {
				console.error("API Error:", err);
				error = "Failed to get prediction. Ensure backend is running.";
			} finally {
				loading = false;
			}
		}, 'image/jpeg', 0.8);
	}

	function reset() {
		capturedImage = null;
		prediction = null;
		error = null;
		startCamera();
	}
</script>

<!-- Main Container with Custom Background -->
<div 
    class="min-h-screen flex flex-col items-center justify-center p-4 font-sans"
    style="background-image: url('/bg.jpg'); background-size: 400px; background-repeat: repeat;"
>
    <!-- Dark Overlay to improve text readability if background is too loud -->
    <div class="fixed inset-0 bg-black/10 pointer-events-none"></div>

    <!-- Main Card with Glass Effect -->
	<div class="relative bg-white/95 backdrop-blur-sm p-6 rounded-2xl shadow-2xl w-full max-w-md border border-white/50">
        
        <!-- Header -->
        <div class="text-center mb-6">
            <h1 class="text-4xl font-extrabold text-yellow-500 drop-shadow-sm">
                Banana Scanner
            </h1>
            <p class="text-gray-500 text-sm mt-1">AI Ripeness Detector</p>
        </div>

		<!-- Camera/Preview Area -->
		<div class="relative w-full aspect-square bg-gray-900 rounded-xl overflow-hidden mb-6 shadow-inner border-4 border-gray-100">
			{#if !capturedImage}
				<video
					bind:this={video}
					class="w-full h-full object-cover"
					autoplay
					muted
					playsinline
				>
                    <track kind="captions">
                </video>
				{#if !stream}
					<div class="absolute inset-0 flex flex-col items-center justify-center bg-gray-100/10 backdrop-blur-md">
                        <div class="bg-white p-4 rounded-full shadow-lg mb-4">
                            <span class="text-4xl">🍌</span>
                        </div>
						<button
							on:click={startCamera}
							class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-full font-bold shadow-lg transform transition hover:scale-105 active:scale-95"
						>
							Start Camera
						</button>
					</div>
				{/if}
			{:else}
				<img src={capturedImage} alt="Captured Banana" class="w-full h-full object-contain" />
			{/if}
            <canvas bind:this={canvas} class="hidden"></canvas>
		</div>

		<!-- Controls -->
		<div class="flex flex-col gap-3">
			{#if error}
				<div class="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded text-sm" role="alert">
					<p class="font-bold">Error</p>
					<p>{error}</p>
				</div>
			{/if}

			{#if stream && !capturedImage}
				<button
					on:click={captureImage}
					class="w-full bg-yellow-400 hover:bg-yellow-500 text-yellow-900 text-xl font-bold py-4 rounded-xl shadow-md transition transform active:scale-95 flex items-center justify-center gap-2"
				>
                    <span>📸</span> Snap Photo
				</button>
			{/if}

			{#if capturedImage && !prediction && !loading}
				<div class="grid grid-cols-2 gap-3">
					<button
						on:click={reset}
						class="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 rounded-xl transition"
					>
						Retake
					</button>
					<button
						on:click={getPrediction}
						class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl shadow-lg transition transform active:scale-95"
					>
						Analyze Ripeness
					</button>
				</div>
			{/if}

			{#if loading}
                <div class="flex flex-col items-center justify-center py-6 space-y-3">
                    <div class="w-8 h-8 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
                    <span class="text-gray-500 font-medium animate-pulse">Consulting the Banana Gods...</span>
                </div>
			{/if}
		</div>

		<!-- Results Display -->
		{#if prediction}
			<div class="mt-6 pt-6 border-t border-dashed border-gray-300 animate-fade-in-up">
				<div class="bg-green-50 border border-green-200 rounded-xl p-5 relative overflow-hidden">
                    <!-- Decorative background icon -->
                    <div class="absolute -right-4 -bottom-4 text-8xl opacity-10 pointer-events-none">✨</div>
                    
					<div class="relative z-10">
                        <h2 class="text-sm uppercase tracking-wide text-green-600 font-bold mb-1">Diagnosis</h2>
                        <p class="text-2xl font-extrabold text-green-900 mb-2">
                            {prediction.class}
                        </p>
                        
                        <div class="flex items-center gap-2 mb-3">
                            <span class="text-2xl">⏳</span>
                            <div>
                                <p class="text-xs text-gray-500 uppercase font-semibold">Time Left</p>
                                <p class="font-bold text-gray-800">{prediction.days_left}</p>
                            </div>
                        </div>

                        <p class="text-sm text-gray-600 bg-white/60 p-3 rounded-lg italic border-l-4 border-green-400">
                            "{prediction.message}"
                        </p>
                    </div>
				</div>
                
                <div class="mt-2 flex justify-between items-center px-2">
                    <span class="text-xs text-gray-400 font-mono">Confidence: {(prediction.confidence * 100).toFixed(1)}%</span>
                    <button
                        on:click={reset}
                        class="text-blue-600 text-sm font-semibold hover:underline"
                    >
                        Scan Another Banana &rarr;
                    </button>
                </div>
			</div>
		{/if}
	</div>
    
    <!-- Footer -->
    <div class="mt-8 text-white/80 text-xs font-medium text-center drop-shadow-md">
        <p>Powered by PyTorch & ONNX</p>
    </div>
</div>

<style>
    /* Simple fade animation for results */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in-up {
        animation: fadeInUp 0.5s ease-out forwards;
    }
</style>