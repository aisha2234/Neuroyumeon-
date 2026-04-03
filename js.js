fetch("http://localhost:8000/city-summary", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    traffic: {"ул. Абая": 85, "пр. Достык": 40},
    emergency: {"Скорая": 1, "Пожарная": 5},
    weather_city: "Almaty"
  })
})
.then(res => res.json())
.then(data => console.log(data.executive_summary));