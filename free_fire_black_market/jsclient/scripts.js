fetch("http://127.0.0.1:8000/api/info/")
  .then((e) => e.json())

  .then((e) => console.log(e))
  .catch((error) => console.log(error));
