function handleRoomButton(url, args) {
    console.log(url)
    window.location.href = url;
    fetch(url, args).then(async r => {
        if (!r.ok) return;

        r.text().then(r => {
            document.getElementById('main-frame').innerHTML = r;
        })
    })
}