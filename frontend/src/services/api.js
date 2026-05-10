export async function getPrediction(input) {
  const res = await fetch("https://cold-start-optimizer-cc.onrender.com/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input)
  });
  return res.json();
}