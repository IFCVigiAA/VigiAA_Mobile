import { createNativeStackNavigator } from '@react-navigation/native-stack';

import ChangePasswordScreen from '../screens/Auth/ChangePasswordScreen';
import ForgotPasswordScreen from '../screens/Auth/ForgotPasswordScreen';
import LoginScreen from '../screens/Auth/LoginScreen';
import RegisterScreen from '../screens/Auth/RegisterScreen';
import FormCaso from '../screens/Forms/CaseFormScreen';
import FormFoco from '../screens/Forms/FocusFormScreen';
import FormCasoPositivo from '../screens/Forms/PositiveCaseFormScreen';
import SintomasScreen from '../screens/Main/SintomasScreen';
import TabNavigator from './TabNavigator';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  return (
    <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
      <Stack.Screen name="ChangePassword" component={ChangePasswordScreen} />
      <Stack.Screen name="MainApp" component={TabNavigator} />
      <Stack.Screen name="Sintomas" component={SintomasScreen} />
      <Stack.Screen name="FormFoco" component={FormFoco} />
      <Stack.Screen name="FormCaso" component={FormCaso} />
      <Stack.Screen name="FormCasoPositivo" component={FormCasoPositivo} />
    </Stack.Navigator>
  );
}