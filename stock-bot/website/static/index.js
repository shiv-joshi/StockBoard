function deleteNote(stockId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ stockId: stockId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}