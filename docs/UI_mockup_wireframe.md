# React Component Analysis: Agent Manager UI

This document breaks down the components of the Agent Manager UI, based on the code in `src/App.tsx`. The application is built as a single large component, but for the purpose of this analysis, it has been divided into its logical, constituent parts.

---

## Table of Contents

1.  [**`App` (Root Component)_**](#app-root-component)
2.  [**`Header`**](#header)
3.  [**`Sidebar`**](#sidebar)
4.  [**`Main Content Area`**](#main-content-area)
5.  [**`Dashboard Page`**](#dashboard-page)
6.  [**`Tasks Page`**](#tasks-page)
7.  [**`Logs Page`**](#logs-page)
8.  [**`Artifacts Page`**](#artifacts-page)
9.  [**`Analytics Page`**](#analytics-page)
10. [**`Settings Page`**](#settings-page)
11. [**`CommandPalette`**](#commandpalette)
12. [**`Button`**](#button)
13. [**`Notifications`**](#notifications)

---

## 1. `App` (Root Component)

*   **Description:**
    The `App` component is the root of the application, a single, all-encompassing component that manages the entire UI and its state. It initializes and controls all the application's data, including the list of agents, chat messages, logs, and user settings. It uses state to dynamically render different "pages" and manages global features like dark mode and sidebar visibility.

*   **UI Placement:**
    As the root component, it wraps the entire application. All other components are rendered within it.

*   **Interdependencies:**
    *   **State Management:** Manages numerous state variables using `useState`, including `activePage`, `darkMode`, `sidebarCollapsed`, `agents`, `chatMessages`, `logs`, etc.
    *   **Child Components:** Renders all other logical components based on its state. For example, it shows the `Dashboard Page` when `activePage` is 'dashboard'.
    *   **Event Handling:** Contains the primary logic for handling events, such as keyboard shortcuts (`useEffect` for `⌘K`), and simulates real-time data updates for agents and notifications.

*   **Markdown Mockup:**
    ```
    +-------------------------------------------------------------------+
    | [Header: Title, Status, Controls]                                 |
    +-------------------------------------------------------------------+
    | [Sidebar] | [Main Content Area: (Active Page Content)]            |
    |           |                                                       |
    |           |                                                       |
    |           |                                                       |
    |           |                                                       |
    +-------------------------------------------------------------------+
    | (Command Palette - shown conditionally)                           |
    +-------------------------------------------------------------------+
    ```

---

## 2. `Header`

*   **Description:**
    The `Header` is the top bar of the application. It provides branding, key status indicators, and global UI controls. It displays the application title ("Agent Manager"), connection status, overall agent system status, and statistics like active agents and task queue size. It also contains buttons to toggle the command palette, collapse the sidebar, and switch between light and dark modes.

*   **UI Placement:**
    Fixed at the top of the screen.

*   **Interdependencies:**
    *   **Relies on `App` state:** `connectionStatus`, `agents`, `sidebarCollapsed`, `darkMode`.
    *   **Triggers `App` actions:** `setShowCommandPalette`, `setSidebarCollapsed`, `setDarkMode`.

*   **Markdown Mockup:**
    ```
    +--------------------------------------------------------------------------------+
    | [Logo] Agent Manager | [Icon] Connected | [Icon] Running | Active: 6/10 | Queue: 15 | [⌘K] [<-] [🌙] |
    +--------------------------------------------------------------------------------+
    ```

---

## 3. `Sidebar`

*   **Description:**
    The `Sidebar` is the primary navigation element of the application. It presents a list of navigable pages, each with an icon and a name. It can be collapsed to a smaller, icon-only view to save space. When collapsed, hovering over an icon reveals a tooltip with the page name.

*   **UI Placement:**
    On the left side of the screen.

*   **Interdependencies:**
    *   **Relies on `App` state:** `activePage` (to highlight the current page), `sidebarCollapsed`.
    *   **Triggers `App` actions:** `setActivePage(pageId)`.

*   **Markdown Mockup (Expanded):**
    ```
    +------------------+
    | [Icon] Dashboard |
    | [Icon] Tasks     |
    | [Icon] Logs      |
    | [Icon] Artifacts |
    | [Icon] Analytics |
    | [Icon] Settings  |
    +------------------+
    ```

---

## 4. `Main Content Area`

*   **Description:**
    This is the main container for the content of the currently selected page. It dynamically renders one of the page components based on the `activePage` state variable from the `App` component.

*   **UI Placement:**
    To the right of the `Sidebar`, occupying the majority of the screen space.

*   **Interdependencies:**
    *   **Relies on `App` state:** `activePage`.
    *   **Renders:** One of the page components (`Dashboard`, `Tasks`, `Logs`, etc.).

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    |                                                     |
    |         (Content of the active page appears here)   |
    |                                                     |
    |                                                     |
    +-----------------------------------------------------+
    ```

---

## 5. `Dashboard Page`

*   **Description:**
    The `Dashboard` provides a high-level overview of the agent system's activity. It features a real-time chat/log feed showing system messages, agent actions, and user inputs. Below the chat, it displays a grid of all agents, showing their ID, role, status, and task queue statistics. Agents' cards can be expanded to view more details.

*   **UI Placement:**
    Rendered in the `Main Content Area` when `activePage` is 'dashboard'.

*   **Interdependencies:**
    *   **Relies on `App` state:** `chatMessages`, `agents`.
    *   **Triggers `App` actions:** `setChatMessages` (when a user sends a message), `toggleAgentExpand`.

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    | Dashboard                                           |
    | +-------------------------------------------------+ |
    | | [Chat/Log Feed]                                 | |
    | | > Agent 1 started: "Research topic"             | |
    | | > You: Do it faster!                            | |
    | | [__________________________________] [Send]      | |
    | +-------------------------------------------------+ |
    | Agents                                              |
    | +------------+ +------------+ +------------+        |
    | | Agent 1    | | Agent 2    | | Agent 3    |        |
    | | [Working]  | | [Idle]     | | [Error]    |        |
    | +------------+ +------------+ +------------+        |
    +-----------------------------------------------------+
    ```

---

## 6. `Tasks Page`

*   **Description:**
    The `Tasks Page` provides a more detailed view of individual tasks in the system. It displays a table of tasks with columns for the task name, its current status (e.g., Done, WIP, Error), the role of the agent assigned to it, duration, and any relevant feedback.

*   **UI Placement:**
    Rendered in the `Main Content Area` when `activePage` is 'tasks'.

*   **Interdependencies:**
    *   Uses a hardcoded list of tasks for demonstration purposes. In a real application, it would depend on a `tasks` state variable from the `App` component.

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    | Task Monitor                            [Filter] [Refresh] |
    | +-------------------------------------------------+ |
    | | Task Name      | Status | Agent Role | Duration | |
    | |----------------|--------|------------|----------| |
    | | Scrape sites   | Done   | Researcher | 2m 10s   | |
    | | Draft post     | WIP    | Writer     | -        | |
    | +-------------------------------------------------+ |
    +-----------------------------------------------------+
    ```

---

## 7. `Logs Page`

*   **Description:**
    The `Logs Page` presents a raw, unfiltered stream of system logs in a dark, terminal-like interface. It's designed for debugging and low-level monitoring. The logs are displayed in JSONL format.

*   **UI Placement:**
    Rendered in the `Main Content Area` when `activePage` is 'logs'.

*   **Interdependencies:**
    *   **Relies on `App` state:** `logs`.

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    | System Logs                             [Export]    |
    | +-------------------------------------------------+ |
    | | {"agent":"System","task":"boot",...}             | |
    | | {"agent":"Agent1","task":"start",...}            | |
    | |                                                 | |
    | +-------------------------------------------------+ |
    +-----------------------------------------------------+
    ```

---

## 8. `Artifacts Page`

*   **Description:**
    The `Artifacts Page` is where users can find and download files generated by the agents. It's organized into categories (Requirements, Design, Development, etc.) using a tabbed navigation system. The "Development" tab features a file tree view to navigate source code and documentation folders. Other tabs display a simple table of artifacts.

*   **UI Placement:**
    Rendered in the `Main Content Area` when `activePage` is 'artifacts'.

*   **Interdependencies:**
    *   **Relies on `App` state:** `activeArtifactTab`, `expandedFolders`.
    *   **Triggers `App` actions:** `setActiveArtifactTab`, `toggleFolder`.
    *   Uses a hardcoded `artifactsData` object for content.

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    | Project Artifacts                      [Upload]     |
    | +-------------------------------------------------+ |
    | | [Reqs] [Design] [Development] [Testing] ...     | |
    | |-------------------------------------------------| |
    | | > source_code/                                  | |
    | |   - main.py                         [Download]  | |
    | |   - utils.py                        [Download]  | |
    | +-------------------------------------------------+ |
    +-----------------------------------------------------+
    ```

---

## 9. `Analytics Page`

*   **Description:**
    The `Analytics Page` provides a high-level dashboard for monitoring system performance through key metrics and charts. It includes summary cards for metrics like total tasks, success rate, and active agents. It also contains placeholders for charts visualizing task completion trends and agent performance.

*   **UI Placement:**
    Rendered in the `Main Content Area` when `activePage` is 'analytics'.

*   **Interdependencies:**
    *   Uses hardcoded data for the metrics cards and agent performance list. The charts are currently placeholders.

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    | Analytics Dashboard                [Last 24 Hours]  |
    | +------------------+ +------------------+           |
    | | Total Tasks      | | Success Rate     | ...       |
    | | 1,247   +12%     | | 94.2%   +2.1%    |           |
    | +------------------+ +------------------+           |
    | +------------------+ +------------------+           |
    | | Task Trend Chart | | Agent Performance|           |
    | | [    Chart     ] | | - Agent 1: 15    |           |
    | +------------------+ +------------------+           |
    +-----------------------------------------------------+
    ```

---

## 10. `Settings Page`

*   **Description:**
    The `Settings Page` allows users to configure the behavior of the agent system. It's divided into two main sections: "Agent Configuration," where users can manage settings for each individual agent (e.g., by uploading a configuration file), and "System Configuration," which contains global settings like the maximum number of agents and health check intervals.

*   **UI Placement:**
    Rendered in the `Main Content Area` when `activePage` is 'settings'.

*   **Interdependencies:**
    *   **Relies on `App` state:** `agents`.
    *   The input fields are currently uncontrolled and do not modify the application state.

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    | Settings                                [Save]      |
    | Agent Configuration                                 |
    | +------------------+ +------------------+           |
    | | Agent 1          | | Agent 2          | ...       |
    | | [Upload File]    | | [Upload File]    |           |
    | +------------------+ +------------------+           |
    | System Configuration                                |
    |  Max Agents [ 10 ]   Health Interval [ 10000 ]      |
    +-----------------------------------------------------+
    ```

---

## 11. `CommandPalette`

*   **Description:**
    The `CommandPalette` is a modal overlay that provides a quick, keyboard-driven way to navigate the app and execute commands. It's activated by a button in the header or the `⌘K` shortcut. It features a search input to filter a list of available commands, such as switching pages or toggling dark mode.

*   **UI Placement:**
    Appears as a modal overlay on top of the entire application when active.

*   **Interdependencies:**
    *   **Relies on `App` state:** `showCommandPalette`.
    *   **Triggers `App` actions:** `setShowCommandPalette(false)`, and various other actions depending on the command selected (e.g., `setActivePage`).

*   **Markdown Mockup:**
    ```
    +-----------------------------------------------------+
    |                                                     |
    |      +-----------------------------------------+    |
    |      | [Search] Type a command...              |    |
    |      |-----------------------------------------|    |
    |      | Go to Dashboard                  [⌘1]   |    |
    |      | Toggle Dark Mode                 [⌘D]   |    |
    |      +-----------------------------------------+    |
    |                                                     |
    +-----------------------------------------------------+
    ```

---

## 12. `Button`

*   **Description:**
    A generic, reusable button component designed with several visual styles (`variant`), sizes (`size`), and a `loading` state. This component is used throughout the application to ensure a consistent look and feel for interactive elements.

*   **UI Placement:**
    Used in various places across different pages, such as the chat input, settings page, and task monitor.

*   **Interdependencies:**
    *   This is a presentational component. Its behavior is determined by the props (`onClick`, etc.) passed to it by its parent component.

*   **Markdown Mockup:**
    ```
    A standard button:
    +---------------+
    | [Save Changes]|
    +---------------+

    A button with an icon:
    +-----------------+
    | [Icon] [Refresh]|
    +-----------------+
    ```

---

## 13. `Notifications`

*   **Description:**
    The `Notifications` system displays small, temporary pop-up messages to alert the user of important events, such as an agent starting a task or encountering an error. Notifications appear for a few seconds and then automatically disappear. They are styled differently based on the type of notification (e.g., info or error).

*   **UI Placement:**
    Appears in the top-right corner of the screen, below the header.

*   **Interdependencies:**
    *   **Relies on `App` state:** `notifications`.
    *   The `App` component's `useEffect` hook manages adding and removing notifications.

*   **Markdown Mockup:**
    ```
    (Appears in top-right corner)

    +----------------------------------------+
    | [Icon] Agent 1 started working         |
    +----------------------------------------+

    +----------------------------------------+
    | [Icon] Agent 3 encountered an error    |
    +----------------------------------------+
    ```
