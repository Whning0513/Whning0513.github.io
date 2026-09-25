(() => {
  "use strict";

  const input = document.querySelector("#note-search");
  const form = document.querySelector("#notes-search");
  const clearButton = document.querySelector("#clear-note-search");
  const status = document.querySelector("#note-search-status");
  const groups = [...document.querySelectorAll(".archive-group")];
  const notes = groups.flatMap((group) =>
    [...group.querySelectorAll(".note-row")].map((note) => ({
      group,
      note,
      text: note.textContent.toLocaleLowerCase(),
    })),
  );

  const update = () => {
    const query = input.value.trim().toLocaleLowerCase();
    let visibleCount = 0;

    notes.forEach(({ note, group, text }) => {
      const matches = !query || text.includes(query);
      note.hidden = !matches;
      if (matches) visibleCount += 1;
      group.hidden = !group.querySelector(".note-row:not([hidden])");
    });

    clearButton.hidden = !query;
    if (!query) {
      status.textContent = `${visibleCount} notes`;
    } else if (visibleCount === 0) {
      status.textContent = "No notes match that search.";
    } else {
      status.textContent = `${visibleCount} note${visibleCount === 1 ? "" : "s"} found`;
    }
  };

  form.addEventListener("submit", (event) => event.preventDefault());
  input.addEventListener("input", update);
  clearButton.addEventListener("click", () => {
    input.value = "";
    input.focus();
    update();
  });

  update();
})();
