const state = {
  token: localStorage.getItem("bookingToken") || "",
  user: JSON.parse(localStorage.getItem("bookingUser") || "null"),
};

const loginForm = document.querySelector("#loginForm");
const usernameInput = document.querySelector("#username");
const passwordInput = document.querySelector("#password");
const logoutButton = document.querySelector("#logoutButton");
const sessionStatus = document.querySelector("#sessionStatus");
const bookingDateInput = document.querySelector("#bookingDate");
const refreshButton = document.querySelector("#refreshButton");
const reloadBookingsButton = document.querySelector("#reloadBookingsButton");
const message = document.querySelector("#message");
const availability = document.querySelector("#availability");
const myBookings = document.querySelector("#myBookings");
const roomsCount = document.querySelector("#roomsCount");

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function formatTime(value) {
  return value.slice(0, 5);
}

function setMessage(text, type = "") {
  message.textContent = text;
  message.className = type;
}

function setSession() {
  if (state.user) {
    sessionStatus.textContent = `${state.user.username} (${state.user.role})`;
    logoutButton.disabled = false;
    return;
  }

  sessionStatus.textContent = "Не выполнен вход";
  logoutButton.disabled = true;
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof data === "object" && data !== null ? data.detail : data;
    throw new Error(detail || `HTTP ${response.status}`);
  }

  return data;
}

async function login(event) {
  event.preventDefault();
  setMessage("Выполняется вход...");

  const body = new URLSearchParams();
  body.set("username", usernameInput.value);
  body.set("password", passwordInput.value);

  try {
    const tokenData = await api("/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    state.token = tokenData.access_token;
    localStorage.setItem("bookingToken", state.token);

    state.user = await api("/auth/me");
    localStorage.setItem("bookingUser", JSON.stringify(state.user));

    setSession();
    setMessage("Вход выполнен.", "success");
    await refreshAll();
  } catch (error) {
    setMessage(error.message, "error");
  }
}

function logout() {
  state.token = "";
  state.user = null;
  localStorage.removeItem("bookingToken");
  localStorage.removeItem("bookingUser");
  setSession();
  roomsCount.textContent = "";
  availability.className = "availability empty-state";
  availability.textContent = "Войдите, чтобы увидеть расписание.";
  myBookings.className = "booking-list empty-state";
  myBookings.textContent = "Пока нет данных.";
  setMessage("Вы вышли из системы.");
}

async function refreshAll() {
  if (!state.token) {
    setMessage("Сначала выполните вход.", "error");
    return;
  }

  await Promise.all([loadAvailability(), loadMyBookings()]);
}

async function loadAvailability() {
  const selectedDate = bookingDateInput.value || todayIso();
  setMessage("Загружается расписание...");

  try {
    const rooms = await api(`/rooms/availability?date=${selectedDate}`);
    renderAvailability(rooms);
    setMessage("Расписание обновлено.", "success");
  } catch (error) {
    setMessage(error.message, "error");
  }
}

function renderAvailability(rooms) {
  roomsCount.textContent = `${rooms.length} комнат`;

  if (rooms.length === 0) {
    availability.className = "availability empty-state";
    availability.textContent = "Комнаты не найдены.";
    return;
  }

  availability.className = "availability";
  availability.replaceChildren(
    ...rooms.map((room) => {
      const roomElement = document.createElement("article");
      roomElement.className = "room";

      const title = document.createElement("div");
      title.className = "room-title";

      const roomName = document.createElement("span");
      roomName.textContent = room.room_name;

      const slotsCount = document.createElement("span");
      slotsCount.textContent = `${room.slots.length} слотов`;

      title.append(roomName, slotsCount);

      const slots = document.createElement("div");
      slots.className = "slots";
      slots.replaceChildren(...room.slots.map((slot) => renderSlot(room, slot)));

      roomElement.append(title, slots);
      return roomElement;
    })
  );
}

function renderSlot(room, slot) {
  const slotElement = document.createElement("div");
  slotElement.className = `slot${slot.is_available ? "" : " busy"}`;

  const time = document.createElement("div");
  time.className = "slot-time";
  time.textContent = `${formatTime(slot.start_time)}-${formatTime(slot.end_time)}`;

  const stateElement = document.createElement("div");
  stateElement.className = "slot-state";
  stateElement.textContent = slot.is_available ? "Свободно" : "Занято";

  const button = document.createElement("button");
  button.type = "button";

  if (slot.is_available) {
    button.textContent = "Забронировать";
    button.addEventListener("click", () => createBooking(room.room_id, slot.slot_id));
  } else {
    button.textContent = state.user?.role === "admin" ? "Отменить бронь" : "Недоступно";
    button.disabled = state.user?.role !== "admin" || !slot.booking_id;

    if (state.user?.role === "admin" && slot.booking_id) {
      button.addEventListener("click", () => cancelBooking(slot.booking_id));
    }
  }

  slotElement.append(time, stateElement, button);
  return slotElement;
}

async function createBooking(roomId, slotId) {
  try {
    await api("/bookings", {
      method: "POST",
      body: JSON.stringify({
        room_id: roomId,
        slot_id: slotId,
        booking_date: bookingDateInput.value || todayIso(),
      }),
    });

    setMessage("Бронирование создано.", "success");
    await refreshAll();
  } catch (error) {
    setMessage(error.message, "error");
  }
}

async function loadMyBookings() {
  try {
    const bookings = await api("/bookings/my");
    renderMyBookings(bookings);
  } catch (error) {
    setMessage(error.message, "error");
  }
}

function renderMyBookings(bookings) {
  if (bookings.length === 0) {
    myBookings.className = "booking-list empty-state";
    myBookings.textContent = "У вас пока нет бронирований.";
    return;
  }

  myBookings.className = "booking-list";
  myBookings.replaceChildren(
    ...bookings.map((booking) => {
      const item = document.createElement("article");
      item.className = `booking-item ${booking.status}`;

      const title = document.createElement("strong");
      title.textContent = `Комната #${booking.room_id}, слот #${booking.slot_id}`;

      const meta = document.createElement("div");
      meta.className = "booking-meta";
      meta.textContent = `${booking.booking_date} · ${booking.status}`;

      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "Отменить";
      button.disabled = booking.status === "cancelled";
      button.addEventListener("click", () => cancelBooking(booking.id));

      item.append(title, meta, button);
      return item;
    })
  );
}

async function cancelBooking(bookingId) {
  try {
    await api(`/bookings/${bookingId}`, { method: "DELETE" });
    setMessage("Бронирование отменено.", "success");
    await refreshAll();
  } catch (error) {
    setMessage(error.message, "error");
  }
}

usernameInput.addEventListener("change", () => {
  passwordInput.value = usernameInput.value === "admin" ? "admin123" : "employee123";
});

loginForm.addEventListener("submit", login);
logoutButton.addEventListener("click", logout);
refreshButton.addEventListener("click", refreshAll);
reloadBookingsButton.addEventListener("click", loadMyBookings);

bookingDateInput.value = todayIso();
setSession();

if (state.token) {
  refreshAll();
}
