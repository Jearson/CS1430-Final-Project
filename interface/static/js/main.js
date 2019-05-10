function getGraph() {
    let results = document.getElementById("results").value;
    console.log(results);
    if (results !== "None") {
        document.getElementById("graph").innerHTML = "You selected: " + results;
    }
}