/* Make Help topics keyboard-friendly native disclosure controls. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toctree-wrapper').forEach((list) => {
    const label = list.previousElementSibling;
    if (!label || label.tagName !== 'P') return;
    const details = document.createElement('details');
    details.open = true;
    const summary = document.createElement('summary');
    summary.textContent = label.textContent.trim();
    details.append(summary);
    list.replaceWith(details);
    details.append(list);
    label.remove();
  });
  document.querySelectorAll('.body h2').forEach((heading) => {
    if (/further reading/i.test(heading.textContent)) {
      const details = document.createElement('details');
      details.open = false;
      const summary = document.createElement('summary');
      summary.textContent = heading.textContent.trim();
      details.append(summary);
      let node = heading.nextElementSibling;
      heading.replaceWith(details);
      while (node && !/^H[1-2]$/.test(node.tagName)) {
        const next = node.nextElementSibling;
        details.append(node);
        node = next;
      }
    }
  });
});
