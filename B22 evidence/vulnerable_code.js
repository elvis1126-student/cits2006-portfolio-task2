// the following code is original from http://7nnine.com/booking.html under file call js, view by the browser


function submitBooking(form) {
  var data = {
    firstName: form.querySelector('[name="firstName"]').value.trim(),
    lastName:  form.querySelector('[name="lastName"]').value.trim(),
    phone:     form.querySelector('[name="phone"]').value.trim(),
    email:     form.querySelector('[name="email"]').value.trim(),
    date:      form.querySelector('[name="date"]').value,
    time:      form.querySelector('[name="time"]').value,
    guests:    parseInt(form.querySelector('[name="guests"]').value, 10),
    message:   form.querySelector('[name="message"]').value.trim()
  };

  var submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Sending...';

  fetch('http://7nnine.com/api-admin/sevennnine/booking', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(function(res) { return res.json(); })
  .then(function(result) {
    if (result.code === 200 || result.code === 0) {
      showFormSuccess(form);
    } else {
      showFormError(form, result.msg || 'Submission failed.');
    }
  })
  .catch(function() {
    showFormError(form, 'Network error. Please check your connection and try again.');
  })
  .finally(function() {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Send';
  });
}
