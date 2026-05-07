import { useMemo, useState } from 'react';
import { useChoreBossAuth } from './useChoreBossAuth';
import { useChoreBossDashboard } from './useChoreBossDashboard';

export function useChoreBossApp() {
  const [message, setMessage] = useState<string>('');
  const auth = useChoreBossAuth({
    onMessageChange: setMessage,
    onLogoutCleanup: () => {
      setMessage('Signed out');
    },
  });
  const dashboard = useChoreBossDashboard({
    session: auth.session,
    onMessageChange: setMessage,
  });

  const isAuthenticated = useMemo(() => auth.session !== null, [auth.session]);
  const isAlertMessage = useMemo(() => {
    if (!message) {
      return false;
    }

    return !message.startsWith('Welcome') && message !== 'Loading chores…' && message !== 'Signed out';
  }, [message]);

  return {
    session: auth.session,
    loginForm: auth.loginForm,
    personCreateForm: dashboard.personCreateForm,
    personEditForm: dashboard.personEditForm,
    editingPersonId: dashboard.editingPersonId,
    peopleFormError: dashboard.peopleFormError,
    peopleFormBusy: dashboard.peopleFormBusy,
    chores: dashboard.chores,
    people: dashboard.people,
    loading: auth.loading,
    dashboardLoading: dashboard.dashboardLoading,
    completingChoreId: dashboard.completingChoreId,
    message,
    isAuthenticated,
    isAlertMessage,
    handleLogin: auth.handleLogin,
    handleLogout: auth.handleLogout,
    setLoginName: auth.setLoginName,
    setPin: auth.setPin,
    completeChoreById: dashboard.completeChoreById,
    createPersonFromForm: dashboard.createPersonFromForm,
    startEditPerson: dashboard.startEditPerson,
    cancelEditPerson: dashboard.cancelEditPerson,
    savePerson: dashboard.savePerson,
    deletePersonById: dashboard.deletePersonById,
    updateCreateForm: dashboard.updateCreateForm,
    updateEditForm: dashboard.updateEditForm,
  };
}
