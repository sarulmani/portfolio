// Portfolio.js - Final Production Version

const API_BASE_URL = "https://portfolio-backend.onrender.com";

// ============================================
// Active Section Highlight
// ============================================

const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-menu a");

window.addEventListener("scroll", () => {
  let current = "";

  sections.forEach((sec) => {
    const top = sec.offsetTop - 100;
    const bottom = top + sec.offsetHeight;

    if (scrollY >= top && scrollY < bottom) {
      current = sec.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");

    if (link.getAttribute("href") === "#" + current) {
      link.classList.add("active");
    }
  });
});

// ============================================
// DOM Loaded
// ============================================

document.addEventListener("DOMContentLoaded", function () {
  // ============================================
  // Contact Form Handling
  // ============================================

  const contactForm = document.querySelector(".contact-form form");

  if (contactForm) {
    contactForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formData = {
        name: this.querySelector('input[placeholder="John Doe"]').value,
        email: this.querySelector('input[placeholder="john@example.com"]')
          .value,
        subject: this.querySelector('input[placeholder="Project inquiry"]')
          .value,
        message: this.querySelector("textarea").value,
      };

      // Validation
      if (
        !formData.name ||
        !formData.email ||
        !formData.subject ||
        !formData.message
      ) {
        showNotification("Please fill in all fields", "error");
        return;
      }

      // Button loading state
      const submitBtn = this.querySelector(".send-btn");
      const originalText = submitBtn.innerHTML;

      submitBtn.innerHTML =
        'Sending... <i class="fa-solid fa-spinner fa-spin"></i>';

      submitBtn.disabled = true;

      try {
        const response = await fetch(`${API_BASE_URL}/api/contact`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (result.success) {
          showNotification(result.message, "success");
          this.reset();
        } else {
          showNotification(result.message, "error");
        }
      } catch (error) {
        console.error("Error:", error);

        showNotification("Network error. Please try again.", "error");
      } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      }
    });
  }

  // ============================================
  // Hire Me Button
  // ============================================

  const hireBtn = document.querySelector(".btn-primary");

  if (hireBtn) {
    hireBtn.addEventListener("click", function (e) {
      e.preventDefault();
      openHireModal();
    });
  }

  // ============================================
  // Download CV Tracking
  // ============================================

  const downloadBtns = document.querySelectorAll(".btn-outline[download]");

  downloadBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      console.log("CV downloaded at: " + new Date().toLocaleString());

      fetch(`${API_BASE_URL}/api/track-download`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          timestamp: new Date().toISOString(),
          page: window.location.pathname,
        }),
      }).catch((err) => console.log("Analytics error:", err));
    });
  });

  // ============================================
  // Let's Talk Button
  // ============================================

  const talkBtn = document.querySelector(".talk-btn");

  if (talkBtn) {
    talkBtn.addEventListener("click", function () {
      document.getElementById("contact").scrollIntoView({ behavior: "smooth" });

      setTimeout(() => {
        showNotification("Fill out the form to start a conversation!", "info");
      }, 500);
    });
  }
});

// ============================================
// Hire Modal
// ============================================

function openHireModal() {
  let modal = document.getElementById("hireModal");

  if (!modal) {
    modal = document.createElement("div");

    modal.id = "hireModal";
    modal.className = "modal";

    modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal">&times;</span>

                <h2 style="color: #22C1F1; margin-bottom: 20px;">
                    📋 Quick Hire
                </h2>

                <form id="quickHireForm">

                    <div class="form-group">
                        <label>Your Name *</label>
                        <input type="text" id="hireName" required>
                    </div>

                    <div class="form-group">
                        <label>Your Email *</label>
                        <input type="email" id="hireEmail" required>
                    </div>

                    <div class="form-group">
                        <label>Quick Message</label>

                        <textarea id="hireMessage" rows="3">
I'd like to discuss an opportunity with you!
                        </textarea>

                    </div>

                    <button type="submit" class="send-btn">
                        Send Request
                    </button>

                </form>
            </div>
        `;

    document.body.appendChild(modal);

    // Styles

    const style = document.createElement("style");

    style.textContent = `
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }

            .modal.show {
                display: flex;
            }

            .modal-content {
                background: #111;
                border: 2px solid #22C1F1;
                border-radius: 20px;
                padding: 40px;
                max-width: 400px;
                width: 90%;
                position: relative;
            }

            .close-modal {
                position: absolute;
                top: 10px;
                right: 20px;
                font-size: 28px;
                color: #22C1F1;
                cursor: pointer;
            }
        `;

    document.head.appendChild(style);

    // Close button

    modal.querySelector(".close-modal").addEventListener("click", () => {
      modal.classList.remove("show");
    });

    // Form submit

    modal
      .querySelector("#quickHireForm")
      .addEventListener("submit", async function (e) {
        e.preventDefault();

        const submitBtn = this.querySelector('button[type="submit"]');

        const originalText = submitBtn.innerHTML;

        submitBtn.innerHTML =
          'Sending... <i class="fa-solid fa-spinner fa-spin"></i>';

        submitBtn.disabled = true;

        try {
          const response = await fetch(`${API_BASE_URL}/api/hire-me`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: document.getElementById("hireName").value,
              email: document.getElementById("hireEmail").value,
              message: document.getElementById("hireMessage").value,
            }),
          });

          const result = await response.json();

          if (result.success) {
            showNotification("Request sent successfully!", "success");

            modal.classList.remove("show");

            this.reset();
          } else {
            showNotification("Failed to send request", "error");
          }
        } catch (error) {
          console.error(error);

          showNotification("Network error", "error");
        } finally {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        }
      });

    // Outside click close

    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("show");
      }
    });
  }

  modal.classList.add("show");
}

// ============================================
// Notification System
// ============================================

function showNotification(message, type = "info") {
  const existing = document.querySelector(".portfolio-notification");

  if (existing) {
    existing.remove();
  }

  const notification = document.createElement("div");

  notification.className = `portfolio-notification ${type}`;

  notification.innerHTML = `
        <div class="notification-content">

            <i class="fa-solid ${
              type === "success"
                ? "fa-check-circle"
                : type === "error"
                  ? "fa-exclamation-circle"
                  : "fa-info-circle"
            }"></i>

            <span>${message}</span>

        </div>
    `;

  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${
          type === "success"
            ? "#4CAF50"
            : type === "error"
              ? "#f44336"
              : "#22C1F1"
        };
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        z-index: 1001;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    `;

  if (!document.querySelector("#notification-keyframes")) {
    const style = document.createElement("style");

    style.id = "notification-keyframes";

    style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }

                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }

                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;

    document.head.appendChild(style);
  }

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease forwards";

    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 5000);
}

// ============================================
// Track Download
// ============================================

function trackDownload() {
  console.log("CV downloaded at: " + new Date().toLocaleString());

  fetch(`${API_BASE_URL}/api/track-download`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
    }),
  }).catch((err) => console.log("Tracking failed:", err));
}
