const API_BASE_URL = 'http://localhost:8000'; // Замените на ваш URL бэкенда

// Функция для создания короткой ссылки
const createShortLink = async (fullLink, expiresAt, isAuthenticated) => {
  try {
    const headers = {
      'Content-Type': 'application/json',
    };

    // Добавляем токен, если пользователь авторизован
    if (isAuthenticated) {
      headers.Authorization = `Bearer ${localStorage.getItem('token')}`;
    }

    const response = await fetch(`${API_BASE_URL}/short_link`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        full_link: fullLink,
        expires_at: expiresAt || null,
      }),
    });

    if (!response.ok) throw new Error('Ошибка при создании ссылки');

    const data = await response.json();
    console.log('Ответ сервера:', data); // Логируем ответ для отладки

    if (!data.link?.short_link) {
      throw new Error('Сервер не вернул короткую ссылку');
    }

    return data.link.short_link; // Извлекаем short_link из объекта link
  } catch (error) {
    console.error('Ошибка:', error);
    throw error;
  }
};

// Обработчик формы создания ссылки
document.getElementById('link-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fullLink = document.getElementById('full-link').value;
  const expiresAt = document.getElementById('expires-at').value;
  const isAuthenticated = !!localStorage.getItem('token');

  try {
    const shortLink = await createShortLink(fullLink, expiresAt, isAuthenticated);
    const resultElement = document.getElementById('short-link-result');
    resultElement.style.display = 'block';
    resultElement.innerText = `Короткая ссылка: ${shortLink}`;
  } catch (error) {
    alert('Не удалось создать короткую ссылку: ' + error.message);
  }
});

// Функция для авторизации
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    });

    if (!response.ok) throw new Error('Ошибка авторизации');

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    window.location.href = 'dashboard.html';
  } catch (error) {
    document.getElementById('login-error').style.display = 'block';
    document.getElementById('login-error').innerText = 'Неверное имя пользователя или пароль';
  }
});

// Функция для выхода
document.getElementById('logout-button')?.addEventListener('click', () => {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
});

// Функция для загрузки списка ссылок
const loadLinks = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/all`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) throw new Error('Ошибка при загрузке ссылок');

    const links = await response.json(); // Ответ — это массив ссылок
    const linkList = document.getElementById('link-list');
    linkList.innerHTML = links
      .map(
        (link) => `
      <li class="list-group-item">
        <p><strong>Полная ссылка:</strong> <a href="${link.full_link}" target="_blank">${link.full_link}</a></p>
        <p><strong>Короткая ссылка:</strong> <a href="${API_BASE_URL}/redirect/${link.short_link}" target="_blank">${link.short_link}</a></p>
        <p><strong>Срок действия:</strong> ${link.expires_at || 'Не указан'}</p>
        <p><strong>Статус:</strong> ${link.is_active ? 'Активна' : 'Неактивна'}</p>
        <p><strong>Всего переходов:</strong> ${link.total_clicks}</p>
        <p><strong>Уникальных пользователей:</strong> ${link.unique_clicks}</p>
        <button class="btn btn-danger btn-sm float-end" onclick="deleteLink('${link.short_link}')">Удалить</button>
      </li>
    `
      )
      .join('');
  } catch (error) {
    console.error('Ошибка:', error);
  }
};

// Функция для удаления ссылки
window.deleteLink = async (shortLink) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${shortLink}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) throw new Error('Ошибка при удалении ссылки');

    loadLinks(); // Обновляем список после удаления
  } catch (error) {
    console.error('Ошибка:', error);
  }
};

// Загружаем ссылки при открытии dashboard.html
if (window.location.pathname.endsWith('dashboard.html')) {
  loadLinks();
}