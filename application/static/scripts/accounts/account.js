function showDetails() {
    let details = document.getElementById('update_details');
    details.removeAttribute("hidden");
    details.scrollIntoView();
}


async function removeFromQuiver(skiboard, size){
    var data = {
        'skiboard': skiboard,
        'size': size
    }

    console.log("Removing skiboard from quiver")
    console.log(data);
    try {
        const response = await fetch("/remove-from-quiver/", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });
    
        const result = await response.json();
        console.log("Success:", result);

        document.getElementById(skiboard + '-label').remove();
        document.getElementById(skiboard + '-button').remove();
        document.getElementById(skiboard + '-filler').remove();
    } catch (error) {
        console.error("Error:", error);
        alert("There was an issue with your search query. Please try again.");
    }
}