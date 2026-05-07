import './App.css';
import { AppLayout } from './components/AppLayout';
import { useChoreBossApp } from './hooks/useChoreBossApp';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';

function App() {
  const app = useChoreBossApp();

  return (
    <AppLayout session={app.session} onLogout={app.handleLogout}>
      {app.isAuthenticated && app.session ? (
        <DashboardPage
          loginName={app.session.loginName}
          isAdmin={app.session.is_admin}
          chores={app.chores}
          people={app.people}
          message={app.message}
          peopleFormError={app.peopleFormError}
          dashboardLoading={app.dashboardLoading}
          peopleFormBusy={app.peopleFormBusy}
          completingChoreId={app.completingChoreId}
          editingPersonId={app.editingPersonId}
          personCreateForm={app.personCreateForm}
          personEditForm={app.personEditForm}
          isAlertMessage={app.isAlertMessage}
          onCompleteChore={app.completeChoreById}
          onCreatePerson={app.createPersonFromForm}
          onEditPerson={app.startEditPerson}
          onCancelEditPerson={app.cancelEditPerson}
          onSavePerson={app.savePerson}
          onDeletePerson={app.deletePersonById}
          onCreateFormChange={app.updateCreateForm}
          onEditFormChange={app.updateEditForm}
        />
      ) : (
        <LoginPage
          loginName={app.loginForm.loginName}
          pin={app.loginForm.pin}
          loading={app.loading}
          message={app.message}
          isAlertMessage={app.isAlertMessage}
          onLoginNameChange={app.setLoginName}
          onPinChange={app.setPin}
          onSubmit={app.handleLogin}
        />
      )}
    </AppLayout>
  );
}

export default App;
