from pendium import app

app.run(host=app.config.get("HOST_IP", "0.0.0.0"))
